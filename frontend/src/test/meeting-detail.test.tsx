import { expect, describe, it, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { MeetingDetailPage } from '../pages/MeetingDetailPage';
import type { Meeting } from '../types';

const { apiMock, toastMock } = vi.hoisted(() => ({
  apiMock: { get: vi.fn(), post: vi.fn() },
  toastMock: { error: vi.fn(), success: vi.fn() },
}));

vi.mock('../services/api', () => ({ api: apiMock }));
vi.mock('react-hot-toast', () => ({ default: toastMock }));

const meeting: Meeting = {
  _id: 'm1',
  user_id: 'u1',
  title: 'Weekly team sync',
  audio_url: 'http://localhost:8000/api/media/recording.mp3',
  transcript: 'Riya will share the onboarding checklist by Friday.',
  created_at: '2026-08-21T00:00:00Z',
  action_items: [
    {
      _id: 'a1',
      meeting_id: 'm1',
      task: 'Share onboarding checklist',
      assignee: 'Riya',
      deadline: 'Friday',
      status: 'pending',
      reminder_sent: false,
      created_at: '2026-08-21T00:00:00Z',
    },
    {
      _id: 'a2',
      meeting_id: 'm1',
      task: 'Send sprint update',
      assignee: null,
      deadline: null,
      status: 'overdue',
      reminder_sent: true,
      created_at: '2026-08-21T00:00:00Z',
    },
  ],
};

const renderPage = () =>
  render(
    <MemoryRouter initialEntries={['/meetings/m1']}>
      <Routes>
        <Route path="/meetings/:id" element={<MeetingDetailPage />} />
      </Routes>
    </MemoryRouter>,
  );

describe('MeetingDetailPage data rendering', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the meeting title, transcript, and every action item', async () => {
    apiMock.get.mockResolvedValue({ data: meeting });
    renderPage();

    expect(await screen.findByRole('heading', { name: 'Weekly team sync' })).toBeInTheDocument();
    expect(screen.getByText('Riya will share the onboarding checklist by Friday.')).toBeInTheDocument();
    expect(screen.getByText('Share onboarding checklist')).toBeInTheDocument();
    expect(screen.getByText('Send sprint update')).toBeInTheDocument();
    expect(screen.getByText('Assignee: Riya')).toBeInTheDocument();
    expect(screen.getByText('Assignee: Unassigned')).toBeInTheDocument();
    expect(screen.getByText('Deadline: Friday')).toBeInTheDocument();
    expect(screen.getByText('Deadline: Not specified')).toBeInTheDocument();
    expect(screen.getByText('pending')).toBeInTheDocument();
    expect(screen.getByText('overdue')).toBeInTheDocument();
    const completeButtons = screen.getAllByRole('button', { name: /Mark complete/i });
    expect(completeButtons).toHaveLength(2);
    completeButtons.forEach((button) => expect(button).toBeEnabled());
    expect(screen.getAllByRole('button', { name: /reminder/i })[1]).toHaveTextContent('Reminder sent');
    expect(toastMock.error).not.toHaveBeenCalled();
  });

  it('shows the loading state before the API resolves', async () => {
    apiMock.get.mockReturnValue(new Promise(() => {}));
    renderPage();

    expect(screen.getByText('Loading meeting...')).toBeInTheDocument();
    expect(screen.queryByText('Action items')).not.toBeInTheDocument();
    await waitFor(() => expect(apiMock.get).toHaveBeenCalledTimes(1));
  });

  it('surfaces a failed API request instead of pretending success', async () => {
    apiMock.get.mockRejectedValue(new Error('network down'));
    renderPage();

    expect(await screen.findByText('Meeting not found.')).toBeInTheDocument();
    expect(screen.queryByText('Action items')).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Weekly team sync' })).not.toBeInTheDocument();
    expect(toastMock.error).toHaveBeenCalledWith('Failed to load meeting details');
    expect(apiMock.get).toHaveBeenCalledWith('/meetings/m1');
  });

  it('renders the empty state when a meeting has no action items', async () => {
    apiMock.get.mockResolvedValue({ data: { ...meeting, action_items: [] } });
    renderPage();

    expect(await screen.findByText('No action items found for this meeting.')).toBeInTheDocument();
    expect(screen.queryByText('Share onboarding checklist')).not.toBeInTheDocument();
  });
});
