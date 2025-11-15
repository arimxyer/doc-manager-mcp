/**
 * Python Language Adapter
 *
 * Handles Python test detection and metadata extraction:
 * - Test functions: test_*
 * - Test classes: Test*
 * - Docstrings
 * - Hash comments
 */

import type { Tree } from 'web-tree-sitter';
import { BaseLanguageAdapter, type InferredMetadata, type TestLocation, type SyntaxNode, filterNullNodes } from './base.js';

export class PythonAdapter extends BaseLanguageAdapter {
  getLanguage(): string {
    return 'python';
  }

  getExtensions(): string[] {
    return ['.py', '.pyi'];
  }

  async getTreeSitterLanguage(): Promise<string> {
    // Return path to WASM file
    return require.resolve('tree-sitter-python/tree-sitter-python.wasm');
  }

  findTestNodes(tree: Tree, sourceCode: string): TestLocation[] {
    const tests: TestLocation[] = [];
    const describeStack: string[] = [];

    const traverse = (node: SyntaxNode) => {
      // Check for test classes (TestSomething)
      if (node.type === 'class_definition') {
        const nameNode = node.childForFieldName('name');
        if (nameNode) {
          const className = sourceCode.slice(nameNode.startIndex, nameNode.endIndex);
          if (className.startsWith('Test')) {
            describeStack.push(className);
            // Traverse children
            for (const child of filterNullNodes(node.children)) {
              traverse(child);
            }
            describeStack.pop();
            return;
          }
        }
      }

      // Check for test functions (test_something)
      if (node.type === 'function_definition') {
        const nameNode = node.childForFieldName('name');
        if (nameNode) {
          const funcName = sourceCode.slice(nameNode.startIndex, nameNode.endIndex);
          if (funcName.startsWith('test_')) {
            tests.push({
              node,
              line: node.startPosition.row + 1,
              testName: funcName,
              describePath: [...describeStack]
            });
          }
        }
      }

      // Continue traversing
      for (const child of filterNullNodes(node.children)) {
        traverse(child);
      }
    };

    traverse(tree.rootNode);
    return tests;
  }

  extractCommentForNode(node: SyntaxNode, sourceCode: string): string {
    const comments: string[] = [];

    // Strategy 1: Check for docstring as first statement in function body
    if (node.type === 'function_definition' || node.type === 'class_definition') {
      const body = node.childForFieldName('body');
      if (body && body.children.length > 0) {
        const firstStatement = filterNullNodes(body.children).find((child) =>
          child.type === 'expression_statement'
        );

        if (firstStatement) {
          const stringNode = filterNullNodes(firstStatement.children).find((child) =>
            child.type === 'string'
          );

          if (stringNode) {
            let docstring = sourceCode.slice(stringNode.startIndex, stringNode.endIndex);
            // Remove quotes (""", ''', ", ')
            docstring = docstring.replace(/^("""|'''|"|')/, '').replace(/("""|'''|"|')$/, '');
            comments.push(docstring.trim());
          }
        }
      }
    }

    // Strategy 2: Check for preceding docstring (expression_statement with string)
    let current = node.previousSibling;

    // Skip whitespace/newline nodes
    while (current && (current.type === 'newline' || current.type === 'indent')) {
      current = current.previousSibling;
    }

    // Check if previous sibling is an expression_statement containing a string (docstring)
    if (current && current.type === 'expression_statement') {
      const stringNode = filterNullNodes(current.children).find((child) =>
        child.type === 'string'
      );

      if (stringNode) {
        let docstring = sourceCode.slice(stringNode.startIndex, stringNode.endIndex);
        // Remove quotes (""", ''', ", ')
        docstring = docstring.replace(/^("""|'''|"|')/, '').replace(/("""|'''|"|')$/, '');
        comments.push(docstring.trim());
      }
    }

    // Strategy 3: Check for comment nodes immediately before the function/class
    current = node.previousSibling;
    const precedingComments: string[] = [];

    while (current && current.type === 'comment') {
      const commentText = sourceCode.slice(current.startIndex, current.endIndex);
      // Remove # prefix
      const cleaned = commentText.replace(/^#\s?/, '').trim();
      precedingComments.unshift(cleaned);
      current = current.previousSibling;
    }

    if (precedingComments.length > 0) {
      comments.push(precedingComments.join('\n'));
    }

    return comments.join('\n');
  }

  generateMetadataComment(metadata: InferredMetadata, indent: string): string {
    const lines: string[] = ['"""'];

    if (metadata.spec) {
      lines.push(`@spec ${metadata.spec}`);
    }

    for (const story of metadata.userStories) {
      lines.push(`@userStory ${story}`);
    }

    for (const req of metadata.functionalReqs) {
      lines.push(`@functionalReq ${req}`);
    }

    lines.push(`@testType ${metadata.testType}`);

    if (metadata.mockDependent) {
      lines.push(`@mockDependent`);
    }

    lines.push('"""');

    return lines.map(line => indent + line).join('\n');
  }

  /**
   * Python-specific mock detection
   */
  isMockDependent(sourceCode: string): boolean {
    const pythonMockPatterns = [
      'unittest.mock',
      'pytest-mock',
      'from unittest.mock import',
      'from unittest import mock',
      '@patch',
      '@mock',
      'Mock(',
      'MagicMock(',
      'mocker.patch'
    ];

    return pythonMockPatterns.some(pattern => sourceCode.includes(pattern)) ||
           super.isMockDependent(sourceCode);
  }

  /**
   * Insert metadata into Python source code
   * Handles decorators and existing docstrings properly
   */
  insertMetadataIntoSource(
    sourceCode: string,
    testNode: SyntaxNode,
    metadata: InferredMetadata
  ): string {
    const lines = sourceCode.split('\n');

    // Get the function body node
    const body = testNode.childForFieldName('body');
    if (!body) {
      throw new Error('Function has no body');
    }

    // Get indentation from function definition line
    const defLine = lines[testNode.startPosition.row];
    const baseIndent = defLine.match(/^\s*/)?.[0] || '';
    const bodyIndent = baseIndent + '    '; // Python uses 4-space indent

    // Check if first statement in body is a docstring
    const firstStatement = filterNullNodes(body.children).find(
      (child) => child.type === 'expression_statement'
    );

    let hasExistingDocstring = false;
    let docstringNode: SyntaxNode | null = null;

    if (firstStatement) {
      const stringNode = filterNullNodes(firstStatement.children).find(
        (child) => child.type === 'string'
      );
      if (stringNode) {
        hasExistingDocstring = true;
        docstringNode = stringNode;
      }
    }

    if (hasExistingDocstring && docstringNode) {
      // Merge metadata into existing docstring
      const docstringLine = docstringNode.startPosition.row;
      const docstringText = lines[docstringLine];

      // Check if it's a multi-line docstring (""")
      if (docstringText.trim().startsWith('"""')) {
        // Find the closing """
        let closingLine = docstringLine;
        for (let i = docstringLine; i < lines.length; i++) {
          if (i > docstringLine && lines[i].includes('"""')) {
            closingLine = i;
            break;
          }
        }

        // Generate metadata lines
        const metadataLines: string[] = [];
        metadataLines.push('');
        if (metadata.spec) metadataLines.push(`${bodyIndent}@spec ${metadata.spec}`);
        for (const story of metadata.userStories) {
          metadataLines.push(`${bodyIndent}@userStory ${story}`);
        }
        for (const req of metadata.functionalReqs) {
          metadataLines.push(`${bodyIndent}@functionalReq ${req}`);
        }
        metadataLines.push(`${bodyIndent}@testType ${metadata.testType}`);
        if (metadata.mockDependent) {
          metadataLines.push(`${bodyIndent}@mockDependent`);
        }

        // Insert metadata before closing """
        lines.splice(closingLine, 0, ...metadataLines);
      }
    } else {
      // No existing docstring - create one as first line of function body
      // Find the line after the function definition (after decorators and def line)
      const bodyStartLine = body.startPosition.row;

      const metadataLines: string[] = [];
      metadataLines.push(`${bodyIndent}"""`);
      if (metadata.spec) metadataLines.push(`${bodyIndent}@spec ${metadata.spec}`);
      for (const story of metadata.userStories) {
        metadataLines.push(`${bodyIndent}@userStory ${story}`);
      }
      for (const req of metadata.functionalReqs) {
        metadataLines.push(`${bodyIndent}@functionalReq ${req}`);
      }
      metadataLines.push(`${bodyIndent}@testType ${metadata.testType}`);
      if (metadata.mockDependent) {
        metadataLines.push(`${bodyIndent}@mockDependent`);
      }
      metadataLines.push(`${bodyIndent}"""`);

      // Insert at the beginning of the function body
      lines.splice(bodyStartLine, 0, ...metadataLines);
    }

    return lines.join('\n');
  }
}
