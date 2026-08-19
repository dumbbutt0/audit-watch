/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testPathIgnorePatterns: ['/node_modules/', '/dist/'],
  testMatch: ['**/tests/**/*.spec.ts'],
  // sandbox PoCs compile + run a full in-process TVM; give them room
  testTimeout: 60000,
};
