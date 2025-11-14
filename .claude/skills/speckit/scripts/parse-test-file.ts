#!/usr/bin/env bun

/**
 * TypeScript Test Parser for Test Registry
 *
 * Parses test files to extract metadata from JSDoc tags:
 * - Test structure (describe/it blocks)
 * - JSDoc tags (@spec, @userStory, @functionalReq, etc.)
 * - File metadata (path, modification date)
 * - Mock dependency detection
 *
 * Outputs JSON array of test metadata objects.
 *
 * Usage:
 *   bun .claude/skills/speckit/scripts/parse-test-file.ts <file-path> [--json]
 *
 * Output:
 *   JSON array of TestMetadata objects
 */

import * as ts from 'typescript';
import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

interface TestMetadata {
  id: string;                      // SHA-256 hash of file+path+name
  file: string;                    // Absolute file path
  type: 'unit' | 'integration' | 'e2e';
  describePath: string[];          // Nested describe blocks
  testName: string;                // it/test block text
  lineNumber: number;              // Start line in file

  // From JSDoc tags
  specNumber: string | null;       // "001", "002", etc.
  userStories: string[];           // ["US1", "US5"]
  functionalReqs: string[];        // ["FR-031", "FR-034"]
  testType: 'unit' | 'integration' | 'e2e' | null;  // Explicit from @testType
  mockDependent: boolean;
  retirementCandidate: boolean;
  contractTest: boolean;
  slow: boolean;

  // File metadata
  createdDate: string;             // ISO 8601
  lastModified: string;            // ISO 8601
  tags: string[];                  // Additional custom tags
}

// Parse command line arguments
const args = process.argv.slice(2);
const FILE_PATH = args.find(arg => !arg.startsWith('--'));
const JSON_MODE = args.includes('--json');

if (!FILE_PATH) {
  console.error('Error: File path required');
  console.error('Usage: parse-test-file.ts <file-path> [--json]');
  process.exit(1);
}

if (!fs.existsSync(FILE_PATH)) {
  console.error(`Error: File not found: ${FILE_PATH}`);
  process.exit(1);
}

// Generate unique test ID
function generateTestId(filePath: string, describePath: string[], testName: string): string {
  const content = `${filePath}::${describePath.join('::')}::${testName}`;
  return crypto.createHash('sha256').update(content).digest('hex').substring(0, 16);
}

// Get string literal value from AST node
function getStringLiteralValue(node: ts.Node | undefined): string {
  if (!node) return '';

  if (ts.isStringLiteral(node)) {
    return node.text;
  }

  if (ts.isNoSubstitutionTemplateLiteral(node)) {
    return node.text;
  }

  if (ts.isTemplateExpression(node)) {
    // For template expressions with substitutions, get the full text
    return node.getText();
  }

  return '';
}

// Extract JSDoc tags from node by parsing comment text
function extractJSDocTags(node: ts.Node, sourceFile: ts.SourceFile): Map<string, string[]> {
  const tags = new Map<string, string[]>();
  const fullText = sourceFile.getFullText();
  const nodeFullStart = node.getFullStart();

  // Get leading trivia (comments before the node)
  const leadingCommentRanges = ts.getLeadingCommentRanges(fullText, nodeFullStart);

  if (!leadingCommentRanges || leadingCommentRanges.length === 0) {
    return tags;
  }

  // Get the last comment (JSDoc should be the last one before the node)
  const lastComment = leadingCommentRanges[leadingCommentRanges.length - 1];
  const commentText = fullText.substring(lastComment.pos, lastComment.end);

  // Check if it's a JSDoc comment (starts with /**)
  if (!commentText.trim().startsWith('/**')) {
    return tags;
  }

  // Parse JSDoc tags using regex
  // Match @tagName value patterns
  const tagRegex = /@(\w+)(?:\s+([^\n@]+))?/g;
  let match;

  while ((match = tagRegex.exec(commentText)) !== null) {
    const tagName = match[1];
    const value = match[2]?.trim() || '';

    if (!tags.has(tagName)) {
      tags.set(tagName, []);
    }

    if (value) {
      tags.get(tagName)!.push(value);
    } else {
      // Flag tags without values (like @mockDependent)
      tags.get(tagName)!.push('true');
    }
  }

  return tags;
}

// Infer test type from file path if not explicitly tagged
function inferTestTypeFromPath(filePath: string): 'unit' | 'integration' | 'e2e' {
  if (filePath.includes('/e2e/') || filePath.includes('.e2e.')) {
    return 'e2e';
  }
  if (filePath.includes('/integration/')) {
    return 'integration';
  }
  return 'unit';
}

// Check if file imports mockAPI
function detectMockDependency(sourceCode: string): boolean {
  return sourceCode.includes('mockAPI') ||
         sourceCode.includes("from '@/api/mock'") ||
         sourceCode.includes('from "../api/mock"') ||
         sourceCode.includes("from '@/lib/api/mock'");
}

// Parse test file and extract metadata
function parseTestFile(filePath: string): TestMetadata[] {
  const sourceCode = fs.readFileSync(filePath, 'utf-8');
  const sourceFile = ts.createSourceFile(
    filePath,
    sourceCode,
    ts.ScriptTarget.Latest,
    true
  );

  const fileStats = fs.statSync(filePath);
  const absolutePath = path.resolve(filePath);
  const tests: TestMetadata[] = [];
  const describePath: string[] = [];
  const fileMockDependent = detectMockDependency(sourceCode);

  // File-level JSDoc tags (inherited by all tests)
  let fileLevelTags: Map<string, string[]> = new Map();
  if (sourceFile.statements.length > 0) {
    const firstStatement = sourceFile.statements[0];
    fileLevelTags = extractJSDocTags(firstStatement, sourceFile);
  }

  function visit(node: ts.Node) {
    // Find describe() calls
    if (ts.isCallExpression(node) &&
        ts.isIdentifier(node.expression) &&
        node.expression.text === 'describe') {

      const describeText = getStringLiteralValue(node.arguments[0]);
      describePath.push(describeText);

      // Visit children within this describe
      ts.forEachChild(node, visit);

      describePath.pop();
      return;
    }

    // Find it() or test() calls
    if (ts.isCallExpression(node) &&
        ts.isIdentifier(node.expression) &&
        (node.expression.text === 'it' || node.expression.text === 'test')) {

      const testName = getStringLiteralValue(node.arguments[0]);
      const lineNumber = sourceFile.getLineAndCharacterOfPosition(node.getStart()).line + 1;

      // Extract JSDoc tags from this test
      const testTags = extractJSDocTags(node, sourceFile);

      // Merge file-level and test-level tags (test-level takes precedence)
      const allTags = new Map(fileLevelTags);
      for (const [key, values] of testTags) {
        allTags.set(key, values);
      }

      // Parse tags
      const specNumber = allTags.get('spec')?.[0] || null;
      const userStories = allTags.get('userStory') || [];
      const functionalReqs = allTags.get('functionalReq') || [];
      const explicitTestType = allTags.get('testType')?.[0] as 'unit' | 'integration' | 'e2e' | undefined;
      const mockDependent = allTags.has('mockDependent') || fileMockDependent;
      const retirementCandidate = allTags.has('retirementCandidate');
      const contractTest = allTags.has('contractTest');
      const slow = allTags.has('slow');

      // Determine test type
      const testType = explicitTestType || inferTestTypeFromPath(absolutePath);

      // Extract all custom tags
      const customTags: string[] = [];
      for (const [tagName] of allTags) {
        if (!['spec', 'userStory', 'functionalReq', 'testType', 'mockDependent',
              'retirementCandidate', 'contractTest', 'slow'].includes(tagName)) {
          customTags.push(tagName);
        }
      }

      // Create test metadata
      const metadata: TestMetadata = {
        id: generateTestId(absolutePath, describePath, testName),
        file: absolutePath,
        type: testType,
        describePath: [...describePath],
        testName,
        lineNumber,
        specNumber,
        userStories,
        functionalReqs,
        testType: explicitTestType || null,
        mockDependent,
        retirementCandidate,
        contractTest,
        slow,
        createdDate: fileStats.birthtime.toISOString(),
        lastModified: fileStats.mtime.toISOString(),
        tags: customTags
      };

      tests.push(metadata);
    }

    // Continue traversing
    ts.forEachChild(node, visit);
  }

  visit(sourceFile);
  return tests;
}

// Main execution
try {
  const tests = parseTestFile(FILE_PATH);

  if (JSON_MODE || true) { // Always output JSON
    console.log(JSON.stringify(tests, null, 2));
  } else {
    console.log(`Parsed ${tests.length} tests from ${FILE_PATH}`);
    for (const test of tests) {
      console.log(`  [${test.type}] ${test.describePath.join(' > ')} > ${test.testName}`);
      console.log(`    Spec: ${test.specNumber || 'none'}`);
      console.log(`    User Stories: ${test.userStories.join(', ') || 'none'}`);
      console.log(`    Functional Reqs: ${test.functionalReqs.join(', ') || 'none'}`);
      console.log('');
    }
  }
} catch (error) {
  console.error('Error parsing test file:', error instanceof Error ? error.message : String(error));
  process.exit(1);
}
