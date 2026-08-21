import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { ExternalLink, FileText, ListTodo } from 'lucide-react';
import { api } from '../services/api';
import { Meeting } from '../types';
import { ActionItemCard } from '../components/ActionItemCard';

export const MeetingDetailPage = () => {
  const { id } = useParams();
  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [loading, setLoading] = useState(true);
  const [mediaLoading, setMediaLoading] = useState(false);

  const loadMeeting = async () => {
    try {
      setLoading(true);
      const { data } = await api.get<Meeting>(`/meetings/${id}`);
      setMeeting(data);
    } catch (error) {
      toast.error('Failed to load meeting details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) loadMeeting();
  }, [id]);

  const handleOpenMedia = async () => {
    if (!meeting?.audio_url) return;
    const popup = window.open('about:blank', '_blank', 'noopener,noreferrer');
    try {
      setMediaLoading(true);
      const rawPath = new URL(meeting.audio_url).pathname;
      const mediaPath = rawPath.replace('/uploads/', '/media/').replace(/^\/api/, '');
      const { data } = await api.get<Blob>(mediaPath, { responseType: 'blob' });
      const objectUrl = URL.createObjectURL(data);
      if (popup) {
        popup.location.href = objectUrl;
        window.setTimeout(() => URL.revokeObjectURL(objectUrl), 60_000);
      } else {
        URL.revokeObjectURL(objectUrl);
        toast.error('Please allow pop-ups to open meeting media');
      }
    } catch {
      popup?.close();
      toast.error('Unable to open meeting media');
    } finally {
      setMediaLoading(false);
    }
  };

  const handleComplete = async (actionItemId: string) => {
    try {
      await api.post(`/action-items/${actionItemId}/complete`);
      toast.success('Action item marked complete');
      loadMeeting();
    } catch {
      toast.error('Unable to mark action item complete');
    }
  };

  const handleReminder = async (actionItemId: string) => {
    try {
      await api.post(`/send-reminder/${actionItemId}`);
      toast.success('Mock reminder sent');
      loadMeeting();
    } catch {
      toast.error('Unable to send reminder');
    }
  };

  if (loading) {
    return <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 text-slate-400">Loading meeting...</div>;
  }

  if (!meeting) {
    return <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 text-slate-400">Meeting not found.</div>;
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_0.95fr]">
      <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-soft">
        <div className="mb-5 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-800 text-brand-100">
              <FileText size={20} />
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-white">{meeting.title}</h2>
              <p className="text-sm text-slate-400">Transcript</p>
            </div>
          </div>
          {meeting.audio_url && (
            <button onClick={handleOpenMedia} disabled={mediaLoading} className="inline-flex items-center gap-2 rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800 disabled:opacity-60">
              <ExternalLink size={16} /> {mediaLoading ? 'Opening...' : 'Open media'}
            </button>
          )}
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-5 text-sm leading-7 text-slate-300 whitespace-pre-wrap">
          {meeting.transcript}
        </div>
      </section>

      <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-soft">
        <div className="mb-5 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-800 text-brand-100">
            <ListTodo size={20} />
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-white">Action items</h2>
            <p className="text-sm text-slate-400">AI-extracted tasks and deadlines</p>
          </div>
        </div>
        <div className="space-y-4">
          {meeting.action_items.length ? meeting.action_items.map((item) => (
            <ActionItemCard key={item._id} item={item} onComplete={handleComplete} onReminder={handleReminder} />
          )) : <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-8 text-center text-slate-400">No action items found for this meeting.</div>}
        </div>
      </section>
    </div>
  );
};
