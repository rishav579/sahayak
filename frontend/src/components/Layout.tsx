import { Bell, LayoutDashboard, LogOut, Settings, UploadCloud } from 'lucide-react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { cn } from '../lib/utils';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/upload', label: 'Upload', icon: UploadCloud },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export const Layout = () => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-7xl gap-6 px-4 py-6 lg:px-8">
        <aside className="hidden w-72 flex-col rounded-3xl border border-slate-800 bg-slate-900/70 p-5 shadow-soft lg:flex">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-500 font-bold">S</div>
            <div>
              <p className="text-xl font-semibold">Sahayak</p>
              <p className="text-sm text-slate-400">Meeting coordinator</p>
            </div>
          </div>
          <nav className="space-y-2">
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition',
                    isActive ? 'bg-brand-500 text-white' : 'text-slate-300 hover:bg-slate-800'
                  )
                }
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="mt-auto rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
            <div className="flex items-center gap-3">
              {user?.picture ? (
                <img src={user.picture} alt={user.name} className="h-12 w-12 rounded-full" />
              ) : (
                <div className="h-12 w-12 rounded-full bg-slate-700" />
              )}
              <div>
                <p className="font-medium">{user?.name}</p>
                <p className="text-xs text-slate-400">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800"
            >
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </aside>

        <main className="flex-1">
          <header className="mb-6 flex items-center justify-between rounded-3xl border border-slate-800 bg-slate-900/70 px-6 py-4 shadow-soft">
            <div>
              <h1 className="text-2xl font-semibold">Namaste, {user?.name?.split(' ')[0] || 'Team'}</h1>
              <p className="text-sm text-slate-400">Track transcripts, tasks, and reminders in one place.</p>
            </div>
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-700 bg-slate-950/60">
              <Bell size={18} />
            </div>
          </header>
          <Outlet />
        </main>
      </div>
    </div>
  );
};
