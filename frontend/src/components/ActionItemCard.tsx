import { CheckCircle2, Clock3, MessageCircleMore } from 'lucide-react';
import { ActionItem } from '../types';
import { statusColor } from '../lib/utils';

export const ActionItemCard = ({
  item,
  onComplete,
  onReminder,
}: {
  item: ActionItem;
  onComplete: (id: string) => void;
  onReminder: (id: string) => void;
}) => {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5 shadow-soft">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-lg font-semibold text-white">{item.task}</p>
          <p className="mt-2 text-sm text-slate-400">Assignee: {item.assignee || 'Unassigned'}</p>
          <p className="mt-1 flex items-center gap-2 text-sm text-slate-400">
            <Clock3 size={14} /> Deadline: {item.deadline || 'Not specified'}
          </p>
        </div>
        <span className={`rounded-full border px-3 py-1 text-xs font-medium capitalize ${statusColor(item.status)}`}>
          {item.status}
        </span>
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          onClick={() => onComplete(item._id)}
          disabled={item.status === 'completed'}
          className="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          <CheckCircle2 size={16} />
          Mark complete
        </button>
        <button
          onClick={() => onReminder(item._id)}
          className="inline-flex items-center gap-2 rounded-xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
        >
          <MessageCircleMore size={16} />
          {item.reminder_sent ? 'Reminder sent' : 'Send WhatsApp reminder'}
        </button>
      </div>
    </div>
  );
};
