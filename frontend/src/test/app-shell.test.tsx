import { expect, describe, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';

describe('App shell', () => {
  it('renders the login screen with the product headline', () => {
    render(<App />);
    const headline = screen.getByRole('heading', { level: 1 });
    expect(headline).toHaveTextContent('Sahayak keeps every meeting clear, actionable, and on time.');
  });

  it('renders the Google sign-in prompt', () => {
    render(<App />);
    expect(screen.getByRole('heading', { name: 'Sign in with Google' })).toBeInTheDocument();
  });
});
