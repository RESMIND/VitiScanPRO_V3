import { expect } from 'vitest';
import * as matchers from '@testing-library/jest-dom/matchers';

// Support both ESM default export and named exports
const resolvedMatchers = (matchers as any).default ?? matchers;
// Use Testing Library's matchers with Vitest's expect
expect.extend(resolvedMatchers);
