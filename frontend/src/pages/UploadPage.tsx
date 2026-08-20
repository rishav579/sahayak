import { DragEvent, useState } from 'react';
import { AudioLines, FileUp, LoaderCircle, UploadCloud } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../services/api';
import { Meeting } from '../types';

export const UploadPage = () => {
  const [title, setTitle] = useState('Weekly team sync');
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<Meeting | null>(null);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped) setFile(dropped);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select an audio or video file.');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('file', file);

    try {
      setLoading(true);
      setProgress(0);
      const { data } = await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (event) => {
          const total = event.total || 1;
          setProgress(Math.round((event.loaded / total) * 100));
        },
      });
      setResult(data.meeting);
      toast.success('Meeting uploaded and processed successfully.');
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Upload failed. Verify backend, MongoDB, and OpenAI configuration.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-soft">
        <h2 className="text-2xl font-semibold text-white">Upload meeting audio/video</h2>
        <p className="mt-2 text-slate-400">Supports Hindi, English, and Hinglish recordings via Whisper transcription.</p>

        <div className="mt-6 grid gap-4 lg:grid-cols-[1fr_320px]">
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={onDrop}
            className={`rounded-3xl border-2 border-dashed p-8 text-center transition ${dragActive ? 'border-brand-500 bg-brand-500/5' : 'border-slate-700 bg-slate-950/50'}`}
          >
            <UploadCloud className="mx-auto mb-4 text-brand-100" size={36} />
            <p className="text-lg font-medium text-white">Drag and drop or choose a recording</p>
            <p className="mt-2 text-sm text-slate-400">MP3, WAV, M4A, MP4, MOV, WEBM up to 50MB</p>
            <input
              type="file"
              accept="audio/*,video/*"
              className="mt-6 block w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-300"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
            {file && <p className="mt-4 inline-flex items-center gap-2 rounded-full bg-slate-900 px-3 py-2 text-sm text-slate-200"><FileUp size={14} /> {file.name}</p>}
          </div>

          <div className="space-y-4 rounded-3xl border border-slate-800 bg-slate-950/60 p-5">
            <div>
              <label className="mb-2 block text-sm text-slate-400">Meeting title</label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none"
              />
            </div>
            <button
              onClick={handleUpload}
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-brand-500 px-4 py-3 font-medium text-white hover:bg-brand-600 disabled:opacity-60"
            >
              {loading ? <LoaderCircle className="animate-spin" size={18} /> : <AudioLines size={18} />}
              {loading ? 'Processing...' : 'Upload and transcribe'}
            </button>
            <div>
              <div className="mb-2 flex justify-between text-sm text-slate-400">
                <span>Progress</span>
                <span>{progress}%</span>
              </div>
              <div className="h-3 overflow-hidden rounded-full bg-slate-800">
                <div className="h-full rounded-full bg-brand-500 transition-all" style={{ width: `${progress}%` }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {result && (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-soft">
          <h3 className="text-xl font-semibold text-white">Latest processed meeting</h3>
          <p className="mt-3 text-slate-300">{result.title}</p>
          <p className="mt-2 text-sm text-slate-400">{result.transcript.slice(0, 250)}...</p>
          <p className="mt-4 text-sm text-brand-100">{result.action_items.length} action items extracted</p>
        </div>
      )}
    </div>
  );
};
