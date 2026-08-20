import clsx from 'clsx';

export const cn = (...inputs: Array<string | false | null | undefined>) => clsx(inputs);

export const statusColor = (status: 'pending' | 'completed' | 'overdue') => {
  switch (status) {
    case 'completed':
      return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30';
    case 'overdue':
      return 'bg-rose-500/15 text-rose-300 border-rose-500/30';
    default:
      return 'bg-amber-500/15 text-amber-300 border-amber-500/30';
  }
};
