import { expect } from 'vitest';
// Ensure jest-dom sees the Vitest expect in the global scope
;(globalThis as any).expect = expect;
import '@testing-library/jest-dom';
