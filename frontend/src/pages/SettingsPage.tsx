import { BadgeInfo, Mail, User2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const SettingsPage = () => {
  const { user } = useAuth();

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-soft">
      <h2 className="text-2xl font-semibold text-white">Settings</h2>
      <p className="mt-2 text-slate-400">Manage your profile and connected account.</p>

      <div className="mt-8 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-5">
          <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-800 text-brand-100">
            <User2 size={20} />
          </div>
          <p className="text-sm text-slate-400">Name</p>
          <p className="mt-1 text-lg font-medium text-white">{user?.name}</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-5">
          <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-800 text-brand-100">
            <Mail size={20} />
          </div>
          <p className="text-sm text-slate-400">Email</p>
          <p className="mt-1 text-lg font-medium text-white">{user?.email}</p>
        </div>
      </div>

      <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/60 p-5">
        <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-800 text-brand-100">
          <BadgeInfo size={20} />
        </div>
        <p className="text-sm text-slate-400">Connected provider</p>
        <p className="mt-1 text-lg font-medium text-white">Google OAuth 2.0</p>
      </div>
    </div>
  );
};
