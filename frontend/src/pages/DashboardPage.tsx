import { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, CheckCircle2, Clock3, FileAudio2, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { api } from '../services/api';
import { ActionItem, Meeting } from '../types';
import { StatCard } from '../components/StatCard';
import { ActionItemCard } from '../components/ActionItemCard';

export const DashboardPage = () => {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [actionItems, setActionItems] = useState<ActionItem[]>([]);
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed' | 'overdue'>('all');
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [meetingsRes, itemsRes] = await Promise.all([
        api.get<Meeting[]>('/meetings'),
        api.get<ActionItem[]>('/action-items'),
      ]);
      setMeetings(meetingsRes.data);
      setActionItems(itemsRes.data);
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const stats = useMemo(() => {
    return {
      pending: actionItems.filter((item) => item.status === 'pending').length,
      completed: actionItems.filter((item) => item.status === 'completed').length,
      overdue: actionItems.filter((item) => item.status === 'overdue').length,
    };
  }, [actionItems]);

  const visibleItems = useMemo(() => {
    if (filter === 'all') return actionItems;
    return actionItems.filter((item) => item.status === filter);
  }, [actionItems, filter]);

  const handleComplete = async (id: string) => {
    try {
      await api.post(`/action-items/${id}/complete`);
      toast.success('Action item marked complete');
      loadData();
    } catch {
      toast.error('Unable to mark action item complete');
    }
  };

  const handleReminder = async (id: string) => {
    try {
      await api.post(`/send-reminder/${id}`);
      toast.success('Mock WhatsApp reminder sent');
      loadData();
    } catch {
      toast.error('Unable to send reminder');
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Pending tasks" value={stats.pending} icon={<Clock3 size={22} />} />
        <StatCard label="Completed tasks" value={stats.completed} icon={<CheckCircle2 size={22} />} />
        <StatCard label="Overdue tasks" value={stats.overdue} icon={<AlertTriangle size={22} />} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-soft">
          <div className="mb-6 flex items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-semibold text-white">Action items</h2>
              <p className="mt-1 text-sm text-slate-400">Track pending, completed, and overdue work.</p>
            </div>
            <div className="flex items-center gap-3">
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as typeof filter)}
                className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-2 text-sm text-slate-200"
              >
                <option value="all">All</option>
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
                <option value="overdue">Overdue</option>
              </select>
              <button onClick={loadData} className="rounded-xl border border-slate-700 px-3 py-2 text-slate-300 hover:bg-slate-800">
                <RefreshCw size={16} />
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {loading ? (
              <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-8 text-center text-slate-400">Loading action items...</div>
            ) : visibleItems.length ? (
              visibleItems.map((item) => (
                <ActionItemCard key={item._id} item={item} onComplete={handleComplete} onReminder={handleReminder} />
              ))
            ) : (
              <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-8 text-center text-slate-400">
                No action items found.
              </div>
            )}
          </div>
        </section>

        <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-soft">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-800 text-brand-100">
              <FileAudio2 size={22} />
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-white">Meetings</h2>
              <p className="text-sm text-slate-400">Recent recordings and transcripts</p>
            </div>
          </div>
          <div className="space-y-4">
            {loading ? (
              <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-8 text-center text-slate-400">Loading meetings...</div>
            ) : meetings.length ? (
              meetings.map((meeting) => (
                <Link
                  key={meeting._id}
                  to={`/meetings/${meeting._id}`}
                  className="block rounded-2xl border border-slate-800 bg-slate-950/60 p-4 transition hover:border-brand-500/30 hover:bg-slate-950"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-medium text-white">{meeting.title}</p>
                      <p className="mt-2 line-clamp-2 text-sm text-slate-400">{meeting.transcript}</p>
                    </div>
                    <span className="rounded-full bg-brand-500/10 px-3 py-1 text-xs text-brand-100">
                      {meeting.action_items.length} tasks
                    </span>
                  </div>
                </Link>
              ))
            ) : (
              <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-8 text-center text-slate-400">
                No meetings uploaded yet.
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};
