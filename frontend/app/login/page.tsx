'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import api from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.login({ email, password });
      router.push('/dashboard');
    } catch (err: any) {
      console.error('Login error:', err);
      if (err.response?.data?.error) {
        setError(err.response.data.error.message);
      } else if (err.message) {
        setError(err.message);
      } else {
        setError('Failed to login. Please check your credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center relative overflow-hidden px-4">
      {/* Animated Background */}
      <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg, #18230F 0%, #27391C 50%, #255F38 100%)' }}>
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-0 -left-4 w-72 h-72 rounded-full mix-blend-multiply filter blur-xl animate-blob" style={{ backgroundColor: '#1F7D53' }}></div>
          <div className="absolute top-0 -right-4 w-72 h-72 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-2000" style={{ backgroundColor: '#255F38' }}></div>
          <div className="absolute -bottom-8 left-20 w-72 h-72 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-4000" style={{ backgroundColor: '#1F7D53' }}></div>
        </div>
      </div>

      {/* Floating shapes */}
      <motion.div
        className="absolute top-20 left-10 w-20 h-20 border-4 border-white/20 rounded-lg"
        animate={{
          y: [0, -20, 0],
          rotate: [0, 180, 360],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      <motion.div
        className="absolute bottom-20 right-10 w-16 h-16 border-4 border-white/20 rounded-full"
        animate={{
          y: [0, 20, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      <div className="w-full max-w-md relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="backdrop-blur-xl bg-white/10 rounded-2xl shadow-2xl p-8 border border-white/20"
        >
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.5 }}
            className="mb-8 text-center"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="inline-block mb-4"
            >
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl shadow-lg transform rotate-6" style={{ background: 'linear-gradient(135deg, #255F38 0%, #1F7D53 100%)' }}>
                🚀
              </div>
            </motion.div>
            <h1 className="text-3xl font-bold text-white mb-2" style={{ backgroundImage: 'linear-gradient(to right, #A8E6CF, #C1F0DC)', backgroundClip: 'text', WebkitBackgroundClip: 'text', color: 'transparent' }}>
              AutoWeb Outreach AI
            </h1>
            <p className="text-green-100">Sign in to your account</p>
          </motion.div>

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mb-4 p-4 bg-red-500/20 backdrop-blur-sm border border-red-400/50 rounded-lg"
            >
              <p className="text-sm text-red-100">{error}</p>
            </motion.div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3, duration: 0.5 }}
            >
              <label
                htmlFor="email"
                className="block text-sm font-medium text-green-100 mb-2"
              >
                Email Address
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg text-white placeholder-green-200/50 focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition-all duration-300"
                placeholder="you@example.com"
                disabled={loading}
              />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4, duration: 0.5 }}
            >
              <label
                htmlFor="password"
                className="block text-sm font-medium text-green-100 mb-2"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg text-white placeholder-green-200/50 focus:ring-2 focus:border-transparent outline-none transition-all duration-300"
                placeholder="••••••••"
                disabled={loading}
              />
            </motion.div>

            <motion.button
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.5 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="w-full text-white py-3 px-4 rounded-lg font-medium shadow-lg hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-transparent transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ background: 'linear-gradient(to right, #255F38, #1F7D53)' }}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Signing in...
                </span>
              ) : (
                'Sign In'
              )}
            </motion.button>
          </form>

          {/* Register Link */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="mt-6 text-center"
          >
            <p className="text-sm text-green-100">
              Don't have an account?{' '}
              <Link
                href="/register"
                className="text-white font-semibold hover:text-green-200 transition-colors underline decoration-2 underline-offset-2"
              >
                Sign up
              </Link>
            </p>
          </motion.div>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7, duration: 0.5 }}
          className="mt-8 text-center"
        >
          <p className="text-sm text-green-100">
            Automated lead generation with AI-powered website previews
          </p>
        </motion.div>
      </div>

      <style jsx>{`
        @keyframes blob {
          0%, 100% {
            transform: translate(0, 0) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}
