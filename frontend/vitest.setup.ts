import { expect } from 'vitest';
// Register jest-dom matchers directly using Vitest's expect
import matchers from '@testing-library/jest-dom/matchers';
expect.extend(matchers as any);
