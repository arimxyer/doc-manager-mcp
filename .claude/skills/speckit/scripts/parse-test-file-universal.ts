#!/usr/bin/env bun

/**
 * Universal Test Parser for Test Registry
 *
 * Parses test files across multiple languages to extract metadata:
 * - Test structure (describe/it blocks, test functions, etc.)
 * - Metadata tags (@spec, @userStory, @functionalReq, etc.)
 * - File metadata (path, modification date)
 * - Mock dependency detection
 *
 * Supported Languages: Python, JavaScript, TypeScript, Go, Rust
 *
 * Outputs JSON array of test metadata objects.
 *
 * Usage:
 *   bun .claude/skills/speckit/scripts/parse-test-file-universal.ts <file-path> [--json]
 *
 * Output:
 *   JSON array of TestMetadata objects
 */

import { Parser, Language } from 'web-tree-sitter';
import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';
import { PythonAdapter } from './language-adapters/python.js';
import { JavaScriptAdapter } from './language-adapters/javascript.js';
import { GoAdapter } from './language-adapters/go.js';
import { RustAdapter } from './language-adapters/rust.js';
import type { LanguageAdapter } from './language-adapters/base.js';

interface TestMetadata {
  id: string;                      // SHA-256 hash of file+path+name
  file: string;                    // Absolute file path
  type: 'unit' | 'integration' | 'e2e';
  describePath: string[];          // Nested describe blocks
  testName: string;                // it/test block text
  lineNumber: number;              // Start line in file

  // From metadata tags
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

  // Test execution results (optional - manually updated after test runs)
  execution?: {
    status: 'passed' | 'failed' | 'skipped' | 'unknown';
    duration: number;              // Seconds
    lastRun: string;               // ISO 8601
    errorMessage: string | null;
  };
}

// Parse command line arguments
const args = process.argv.slice(2);
const FILE_PATH = args.find(arg => !arg.startsWith('--')) as string;
const JSON_MODE = args.includes('--json');

if (!FILE_PATH) {
  console.error('Error: File path required');
  console.error('Usage: parse-test-file-universal.ts <file-path> [--json]');
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

// Detect language adapter based on file extension
function getAdapterForFile(filePath: string): LanguageAdapter | null {
  const ext = path.extname(filePath).toLowerCase();
  const adapters: LanguageAdapter[] = [
    new PythonAdapter(),
    new JavaScriptAdapter(),
    new GoAdapter(),
    new RustAdapter()
  ];

  for (const adapter of adapters) {
    if (adapter.getExtensions().includes(ext)) {
      return adapter;
    }
  }

  return null;
}

// Get file stats
function getFileStats(filePath: string) {
  const stats = fs.statSync(filePath);
  return {
    createdDate: stats.birthtime.toISOString(),
    lastModified: stats.mtime.toISOString()
  };
}

/**
 * Parse a test file and extract metadata
 */
async function parseTestFile(filePath: string): Promise<TestMetadata[]> {
  const adapter = getAdapterForFile(filePath);

  if (!adapter) {
    throw new Error(`Unsupported file type: ${path.extname(filePath)}`);
  }

  // Read file content
  const content = fs.readFileSync(filePath, 'utf-8');

  // Initialize tree-sitter
  await Parser.init();
  const parser = new Parser();
  const wasmPath = await adapter.getTreeSitterLanguage();
  const language = await Language.load(wasmPath);
  parser.setLanguage(language);

  // Parse the file
  const tree = parser.parse(content);

  if (!tree) {
    throw new Error('Failed to parse file');
  }

  // Find all test nodes
  const testLocations = adapter.findTestNodes(tree, content);

  // Get file stats
  const fileStats = getFileStats(filePath);

  // Extract metadata for each test
  const results: TestMetadata[] = [];

  for (const location of testLocations) {
    const { node, line, testName, describePath } = location;

    // Extract comment/docstring for this test
    const commentText = adapter.extractCommentForNode(node, content);

    // Parse tags from comment
    const tags = adapter.extractTags(commentText);

    // Infer test type from file path if not explicitly tagged
    const inferredType = adapter.inferTestType(filePath);
    const testType = tags.testType || inferredType;

    // Check for mock dependencies
    const mockDependent = tags.mockDependent || adapter.isMockDependent(content);

    // Extract custom tags (any tag that's not a standard one)
    const standardTags = ['spec', 'userStory', 'functionalReq', 'testType',
                          'mockDependent', 'retirementCandidate', 'contractTest', 'slow'];
    const customTags = Object.keys(tags).filter(key => !standardTags.includes(key));

    // Create metadata object
    const metadata: TestMetadata = {
      id: generateTestId(path.resolve(filePath), describePath, testName),
      file: path.resolve(filePath),
      type: testType,
      describePath,
      testName,
      lineNumber: line,

      specNumber: tags.spec || null,
      userStories: tags.userStories || [],
      functionalReqs: tags.functionalReqs || [],
      testType: tags.testType || null,
      mockDependent,
      retirementCandidate: tags.retirementCandidate || false,
      contractTest: tags.contractTest || false,
      slow: tags.slow || false,

      createdDate: fileStats.createdDate,
      lastModified: fileStats.lastModified,
      tags: customTags
    };

    results.push(metadata);
  }

  return results;
}

/**
 * Main execution
 */
async function main() {
  try {
    const results = await parseTestFile(FILE_PATH);

    if (JSON_MODE) {
      console.log(JSON.stringify(results, null, 2));
    } else {
      console.log(`Found ${results.length} tests in ${FILE_PATH}`);
      for (const test of results) {
        console.log(`  ${test.testName} (line ${test.lineNumber})`);
        if (test.specNumber) {
          console.log(`    Spec: ${test.specNumber}`);
        }
        if (test.userStories.length > 0) {
          console.log(`    Stories: ${test.userStories.join(', ')}`);
        }
      }
    }
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

main();
