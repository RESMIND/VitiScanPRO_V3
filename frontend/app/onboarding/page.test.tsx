import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
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
    fireEvent.click(screen.getByText('Next')); // step 2 -> phone

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
    const phoneInput = screen.getByPlaceholderText('Phone (+40...)');
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
    fireEvent.click(screen.getByText('Next'));

    // Step 4 - upload
    const file = new File(['logo'], 'logo.png', { type: 'image/png' });
    const input = screen.getByLabelText(/Upload logo/i) || screen.getByRole('textbox') || screen.getByTestId('file-input') || screen.getByPlaceholderText('');
    // Fallback: query input[type=file]
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [file] } });

    fireEvent.click(screen.getByText('Finish onboarding'));

    await waitFor(() => expect(screen.getByText('Onboarding finalized successfully')).toBeInTheDocument());
  });

  it('shows error when onboarding complete fails', async () => {
    (axios.post as any).mockImplementation((url: string) => {
      if (url.includes('/onboarding/complete')) {
        return Promise.reject({ response: { data: { detail: 'Missing fields' } } });
      }
      return Promise.resolve({ data: {} });
    });

    render(<OnboardingPage />);

    fireEvent.click(screen.getByText('Start'));
    fireEvent.click(screen.getByText('Next'));

    // skip verification logic, go to establishment details
    fireEvent.change(screen.getByPlaceholderText('Farm name'), { target: { value: 'F' } });
    fireEvent.click(screen.getByText('Next'));

    fireEvent.click(screen.getByText('Finish onboarding'));

    await waitFor(() => expect(screen.getByText('Missing fields')).toBeInTheDocument());
  });
});
