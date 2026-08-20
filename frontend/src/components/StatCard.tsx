import { ReactNode } from 'react';

export const StatCard = ({ label, value, icon }: { label: string; value: string | number; icon: ReactNode }) => {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5 shadow-soft">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-800 text-brand-100">{icon}</div>
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-white">{value}</p>
    </div>
  );
};
