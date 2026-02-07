/// <reference types="vitest" />
/// <reference types="@testing-library/jest-dom" />
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import axios from 'axios';

import OnboardingPage from './page';

vi.mock('axios');

describe('OnboardingPage', () => {
  beforeEach(() => {
    (axios.post as any).mockReset();
    (axios.get as any).mockReset();
  });

  it('sends verification code and advances on successful verify', async () => {
    (axios.post as any).mockImplementation((url: string) => {
      if (url.includes('/send-verification-code')) {
        return Promise.resolve({ data: { message: 'Code sent' } });
      }
      if (url.includes('/verify-phone-code')) {
        return Promise.resolve({ data: { ok: true } });
      }
      return Promise.resolve({ data: {} });
    });

    render(<OnboardingPage />);

    // Start -> step 2
    fireEvent.click(screen.getByText('Start'));
    expect(screen.getByText('Phone verification')).toBeInTheDocument();

    const phoneInput = screen.getByPlaceholderText('Phone (+40...)');
    fireEvent.change(phoneInput, { target: { value: '+40700123456' } });

    fireEvent.click(screen.getByText('Send code'));

    await waitFor(() => expect(screen.getByText('Code sent')).toBeInTheDocument());

    const codeInput = screen.getByPlaceholderText('Enter code');
    fireEvent.change(codeInput, { target: { value: '1234' } });

    fireEvent.click(screen.getByText('Verify'));

    await waitFor(() => expect(screen.getByText('Establishment details')).toBeInTheDocument());
  });

  it('uploads logo and finishes onboarding (happy path)', async () => {
    (axios.post as any).mockImplementation((url: string) => {
      if (url.includes('/onboarding/complete')) {
        return Promise.resolve({ data: { establishment_id: 'est-1' } });
      }
      if (url.includes('/establishments/est-1/logo')) {
        return Promise.resolve({ data: { ok: true } });
      }
      return Promise.resolve({ data: {} });
    });

    render(<OnboardingPage />);

    // Drive to step 4 by starting and faking verified state
    fireEvent.click(screen.getByText('Start'));
    // Click the first enabled "Next" button (avoids duplicate elements from strict-mode renders)
    const nextButtons = screen.getAllByText('Next');
    const enabledNext = nextButtons.find((b) => !b.hasAttribute('disabled')) || nextButtons[0];
    fireEvent.click(enabledNext); // step 2 -> phone

    // Mock that verification step was completed
    // Actually advance using Next (page allows next only if verified) so we simulate by setting verified via DOM: not straightforward
    // Instead, go through steps using user interactions: fill phone/code and call send/verify
    (axios.post as any).mockImplementation((url: string) => {
      if (url.includes('/send-verification-code')) return Promise.resolve({ data: { message: 'Code sent' } });
      if (url.includes('/verify-phone-code')) return Promise.resolve({ data: { ok: true } });
      if (url.includes('/onboarding/complete')) return Promise.resolve({ data: { establishment_id: 'est-1' } });
      if (url.includes('/establishments/est-1/logo')) return Promise.resolve({ data: { ok: true } });
      return Promise.resolve({ data: {} });
    });

    // fill phone
    const phoneInputs = screen.getAllByPlaceholderText('Phone (+40...)');
    const phoneInput = phoneInputs.find((i) => !i.hasAttribute('disabled')) || phoneInputs[0];
    fireEvent.change(phoneInput, { target: { value: '+40700123456' } });
    fireEvent.click(screen.getByText('Send code'));
    await waitFor(() => expect(screen.getByText('Code sent')).toBeInTheDocument());
    const codeInput = screen.getByPlaceholderText('Enter code');
    fireEvent.change(codeInput, { target: { value: '1234' } });
    fireEvent.click(screen.getByText('Verify'));
    await waitFor(() => expect(screen.getByText('Establishment details')).toBeInTheDocument());

    // Fill establishment details
    fireEvent.change(screen.getByPlaceholderText('Farm name'), { target: { value: 'Ferma Test' } });
    fireEvent.change(screen.getByPlaceholderText('Address'), { target: { value: 'Strada 1' } });
    // Click the first enabled "Next" button to proceed (avoid duplicate Next buttons)
    const nextButtons2 = screen.getAllByText('Next');
    const enabledNext2 = nextButtons2.find((b) => !b.hasAttribute('disabled')) || nextButtons2[0];
    fireEvent.click(enabledNext2);

    // Step 4 - upload
    const file = new File(['logo'], 'logo.png', { type: 'image/png' });
    // Query safely for the file input
    const fileInput = screen.queryByLabelText(/Upload logo/i) as HTMLInputElement | null
      || document.querySelector('input[type="file"]') as HTMLInputElement | null;
    expect(fileInput).not.toBeNull();
    if (fileInput) {
      fireEvent.change(fileInput, { target: { files: [file] } });
    }

    // Click the first enabled "Finish onboarding" button (avoid duplicates from strict-mode)
    const finishButtons = screen.getAllByText('Finish onboarding');
    const finishBtn = finishButtons.find((b) => !b.hasAttribute('disabled')) || finishButtons[0];
    fireEvent.click(finishBtn);

    await waitFor(() => expect(screen.getAllByText('Onboarding finalized successfully').length).toBeGreaterThan(0));
  });

  it('shows error when onboarding complete fails', async () => {
    (axios.post as any).mockImplementation((url: string) => {
      if (url.includes('/send-verification-code')) return Promise.resolve({ data: { message: 'Code sent' } });
      if (url.includes('/verify-phone-code')) return Promise.resolve({ data: { ok: true } });
      if (url.includes('/onboarding/complete')) {
        return Promise.reject({ response: { data: { detail: 'Missing fields' } } });
      }
      return Promise.resolve({ data: {} });
    });

    render(<OnboardingPage />);

    fireEvent.click(screen.getByText('Start'));

    // go through verification so we can reach establishment step
    const phoneInputs2 = screen.getAllByPlaceholderText('Phone (+40...)');
    const phoneInput2 = phoneInputs2.find((i) => !i.hasAttribute('disabled')) || phoneInputs2[0];
    fireEvent.change(phoneInput2, { target: { value: '+40700123456' } });
    fireEvent.click(screen.getByText('Send code'));
    await waitFor(() => expect(screen.getByText('Code sent')).toBeInTheDocument());
    fireEvent.change(screen.getByPlaceholderText('Enter code'), { target: { value: '1234' } });
    fireEvent.click(screen.getByText('Verify'));
    await waitFor(() => expect(screen.getByText('Establishment details')).toBeInTheDocument());

    fireEvent.change(screen.getByPlaceholderText('Farm name'), { target: { value: 'F' } });
    // Click the first enabled "Next" button
    const nextButtons3 = screen.getAllByText('Next');
    const enabledNext3 = nextButtons3.find((b) => !b.hasAttribute('disabled')) || nextButtons3[0];
    fireEvent.click(enabledNext3);

    // Click the first enabled "Finish onboarding" button
    const finishButtons2 = screen.getAllByText('Finish onboarding');
    const finishBtn2 = finishButtons2.find((b) => !b.hasAttribute('disabled')) || finishButtons2[0];
    fireEvent.click(finishBtn2);

    await waitFor(() => expect(screen.getByText('Missing fields')).toBeInTheDocument());
  });
});
