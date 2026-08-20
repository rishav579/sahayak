import { GoogleLogin } from '@react-oauth/google';
import { Mic2, Sparkles, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';

export const LoginPage = () => {
  const { loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="grid w-full max-w-6xl gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-[32px] border border-slate-800 bg-slate-900/70 p-8 shadow-soft lg:p-12">
          <div className="mb-8 inline-flex items-center gap-3 rounded-full border border-brand-500/30 bg-brand-500/10 px-4 py-2 text-sm text-brand-100">
            <Sparkles size={16} /> AI-native meeting coordinator for Indian remote teams
          </div>
          <h1 className="max-w-2xl text-4xl font-semibold leading-tight text-white lg:text-6xl">
            Sahayak keeps every meeting clear, actionable, and on time.
          </h1>
          <p className="mt-6 max-w-2xl text-lg text-slate-300">
            Upload Hindi, English, or Hinglish meeting recordings, get instant transcription, extract action items, and send mock WhatsApp reminders from one dashboard.
          </p>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {[
              'Whisper transcription',
              'GPT action extraction',
              'Reminder tracking',
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4 text-sm text-slate-300">
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-slate-800 text-brand-100">
                  <CheckCircle2 size={18} />
                </div>
                {item}
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-[32px] border border-slate-800 bg-slate-900/70 p-8 shadow-soft lg:p-10">
          <div className="mb-8 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-500 text-white">
            <Mic2 />
          </div>
          <h2 className="text-3xl font-semibold text-white">Sign in with Google</h2>
          <p className="mt-3 text-slate-400">Secure OAuth login to access your meetings, transcripts, and task dashboard.</p>

          <div className="mt-8 flex min-h-20 items-center">
            <GoogleLogin
              onSuccess={async (credentialResponse) => {
                if (!credentialResponse.credential) {
                  toast.error('Google login token missing');
                  return;
                }
                try {
                  await loginWithGoogle(credentialResponse.credential);
                  toast.success('Logged in successfully');
                  navigate('/dashboard');
                } catch (error) {
                  toast.error('Login failed. Please check backend and Google OAuth setup.');
                }
              }}
              onError={() => toast.error('Google login failed')}
              useOneTap
            />
          </div>

          <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-950/60 p-4 text-sm text-slate-400">
            Tip: set your Google Client ID in <code>frontend/.env</code> and backend credentials in <code>backend/.env</code>.
          </div>
        </div>
      </div>
    </div>
  );
};
