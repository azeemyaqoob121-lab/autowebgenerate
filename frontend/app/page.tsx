'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import api from '@/lib/api';

interface Stats {
  total_businesses: number;
  qualified_leads: number;
  templates_generated: number;
}

export default function Home() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch stats without authentication (will show 0s if not logged in)
    const fetchStats = async () => {
      try {
        const data = await api.getStats();
        setStats(data);
      } catch (error) {
        // If not authenticated, show placeholder stats
        setStats({
          total_businesses: 0,
          qualified_leads: 0,
          templates_generated: 0,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg, #18230F 0%, #27391C 50%, #255F38 100%)' }}>
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-0 -left-4 w-96 h-96 rounded-full mix-blend-multiply filter blur-xl animate-blob" style={{ backgroundColor: '#1F7D53' }}></div>
          <div className="absolute top-0 -right-4 w-96 h-96 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-2000" style={{ backgroundColor: '#255F38' }}></div>
          <div className="absolute -bottom-8 left-20 w-96 h-96 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-4000" style={{ backgroundColor: '#1F7D53' }}></div>
        </div>
      </div>

      {/* Floating shapes */}
      <motion.div
        className="absolute top-20 right-20 w-32 h-32 border-4 border-white/10 rounded-full"
        animate={{
          y: [0, -30, 0],
          x: [0, 20, 0],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      <motion.div
        className="absolute bottom-40 left-10 w-24 h-24 border-4 border-white/10 rounded-lg"
        animate={{
          rotate: [0, 90, 0],
          y: [0, 20, 0],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* Content */}
      <div className="relative z-10">
        {/* Hero Section */}
        <section className="min-h-screen flex items-center justify-center px-4 py-20">
          <div className="max-w-6xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="inline-block mb-6"
              >
                <div className="w-20 h-20 rounded-3xl flex items-center justify-center text-4xl shadow-2xl" style={{ background: 'linear-gradient(135deg, #255F38 0%, #1F7D53 100%)' }}>
                  🚀
                </div>
              </motion.div>

              <h1 className="text-5xl md:text-7xl font-bold text-white mb-6" style={{ backgroundImage: 'linear-gradient(to right, #A8E6CF, #C1F0DC)', backgroundClip: 'text', WebkitBackgroundClip: 'text', color: 'transparent' }}>
                AutoWeb Outreach AI
              </h1>

              <p className="text-xl md:text-2xl text-green-100 mb-4 max-w-3xl mx-auto">
                Automated lead generation platform with AI-powered website previews
              </p>

              <p className="text-lg text-green-200/80 mb-12 max-w-2xl mx-auto">
                Discover UK businesses, evaluate their websites, and generate personalized AI templates to win more clients.
              </p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.6 }}
                className="flex flex-col sm:flex-row gap-4 justify-center items-center"
              >
                <Link href="/register">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 text-lg font-semibold text-white rounded-xl shadow-xl hover:shadow-2xl transition-all duration-300"
                    style={{ background: 'linear-gradient(to right, #255F38, #1F7D53)' }}
                  >
                    Get Started Free
                  </motion.button>
                </Link>

                <Link href="/login">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 text-lg font-semibold text-white rounded-xl border-2 border-white/30 backdrop-blur-sm bg-white/10 hover:bg-white/20 transition-all duration-300"
                  >
                    Sign In
                  </motion.button>
                </Link>
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* Stats Section */}
        <section className="py-20 px-4">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-12"
            >
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Platform Activity
              </h2>
              <p className="text-green-100 text-lg">
                Real-time insights into AutoWeb generation
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1, duration: 0.6 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className="backdrop-blur-xl bg-white/10 rounded-2xl p-8 border border-white/20 shadow-xl"
              >
                <div className="text-5xl mb-4">📊</div>
                <h3 className="text-4xl font-bold text-white mb-2">
                  {loading ? '...' : stats?.total_businesses.toLocaleString()}
                </h3>
                <p className="text-green-100 text-lg">Total Businesses</p>
                <p className="text-green-200/70 text-sm mt-2">Discovered and analyzed</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2, duration: 0.6 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className="backdrop-blur-xl bg-white/10 rounded-2xl p-8 border border-white/20 shadow-xl"
              >
                <div className="text-5xl mb-4">🎯</div>
                <h3 className="text-4xl font-bold text-white mb-2">
                  {loading ? '...' : stats?.qualified_leads.toLocaleString()}
                </h3>
                <p className="text-green-100 text-lg">Qualified Leads</p>
                <p className="text-green-200/70 text-sm mt-2">High-potential prospects</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.3, duration: 0.6 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className="backdrop-blur-xl bg-white/10 rounded-2xl p-8 border border-white/20 shadow-xl"
              >
                <div className="text-5xl mb-4">✨</div>
                <h3 className="text-4xl font-bold text-white mb-2">
                  {loading ? '...' : stats?.templates_generated.toLocaleString()}
                </h3>
                <p className="text-green-100 text-lg">AI Templates</p>
                <p className="text-green-200/70 text-sm mt-2">Generated with GPT-4</p>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 px-4">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-12"
            >
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Powerful Features
              </h2>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1, duration: 0.6 }}
                className="backdrop-blur-xl bg-white/10 rounded-2xl p-8 border border-white/20"
              >
                <h3 className="text-2xl font-semibold text-white mb-3 flex items-center gap-3">
                  <span className="text-3xl">🔍</span>
                  Business Discovery
                </h3>
                <p className="text-green-100">
                  Automated scraping of UK business directories to find your ideal clients
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2, duration: 0.6 }}
                className="backdrop-blur-xl bg-white/10 rounded-2xl p-8 border border-white/20"
              >
                <h3 className="text-2xl font-semibold text-white mb-3 flex items-center gap-3">
                  <span className="text-3xl">⚡</span>
                  Website Evaluation
                </h3>
                <p className="text-green-100">
                  Lighthouse-based performance scoring to identify improvement opportunities
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.3, duration: 0.6 }}
                className="backdrop-blur-xl bg-white/10 rounded-2xl p-8 border border-white/20"
              >
                <h3 className="text-2xl font-semibold text-white mb-3 flex items-center gap-3">
                  <span className="text-3xl">🤖</span>
                  AI Template Generation
                </h3>
                <p className="text-green-100">
                  GPT-4 powered website preview generation tailored to each business
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.4, duration: 0.6 }}
                className="backdrop-blur-xl bg-white/10 rounded-2xl p-8 border border-white/20"
              >
                <h3 className="text-2xl font-semibold text-white mb-3 flex items-center gap-3">
                  <span className="text-3xl">🔐</span>
                  Secure Authentication
                </h3>
                <p className="text-green-100">
                  JWT-based authentication with refresh tokens for secure access
                </p>
              </motion.div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-4">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="max-w-4xl mx-auto text-center backdrop-blur-xl bg-white/10 rounded-3xl p-12 border border-white/20"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to automate your lead generation?
            </h2>
            <p className="text-green-100 text-lg mb-8">
              Join now and start discovering qualified leads with AI-powered insights
            </p>
            <Link href="/register">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-10 py-4 text-lg font-semibold text-white rounded-xl shadow-2xl transition-all duration-300"
                style={{ background: 'linear-gradient(to right, #255F38, #1F7D53)' }}
              >
                Get Started Today
              </motion.button>
            </Link>
          </motion.div>
        </section>
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
