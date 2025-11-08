'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import api from '@/lib/api';
import type { Stats } from '@/lib/types';
import Link from 'next/link';

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Fetch real stats from API
        const data = await api.getStats();
        setStats(data);
        setError('');
      } catch (err: any) {
        console.error('Failed to fetch stats:', err);
        setError('Failed to load statistics');
        // Use fallback data on error
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="space-y-8"
    >
      {/* Page Header */}
      <motion.div variants={itemVariants}>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Dashboard
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          Welcome to AutoWeb Outreach AI ✨
        </p>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
      >
        {/* Total Businesses */}
        <motion.div
          whileHover={{ y: -4, boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)' }}
          transition={{ duration: 0.2 }}
          className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl shadow-lg p-6 text-white relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16" />
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-12 -mb-12" />

          <div className="relative">
            <div className="flex items-center justify-between mb-4">
              <span className="text-5xl">🏢</span>
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
            </div>
            <div className="text-sm font-medium text-blue-100 mb-1">Total Businesses</div>
            <div className="text-4xl font-bold mb-4">{stats?.total_businesses || 0}</div>
            <Link
              href="/dashboard/businesses?showAll=true"
              className="inline-flex items-center text-sm font-semibold text-white bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg transition-colors"
            >
              View all
              <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </motion.div>

        {/* Qualified Leads */}
        <motion.div
          whileHover={{ y: -4, boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)' }}
          transition={{ duration: 0.2 }}
          className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl shadow-lg p-6 text-white relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16" />
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-12 -mb-12" />

          <div className="relative">
            <div className="flex items-center justify-between mb-4">
              <span className="text-5xl">🎯</span>
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
            <div className="text-sm font-medium text-purple-100 mb-1">Qualified Leads</div>
            <div className="text-4xl font-bold mb-1">{stats?.qualified_leads || 0}</div>
            <div className="text-xs text-purple-200 mb-3">Score &lt; 70%</div>
            <Link
              href="/dashboard/businesses"
              className="inline-flex items-center text-sm font-semibold text-white bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg transition-colors"
            >
              View leads
              <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </motion.div>

        {/* Templates Generated */}
        <motion.div
          whileHover={{ y: -4, boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)' }}
          transition={{ duration: 0.2 }}
          className="bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl shadow-lg p-6 text-white relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16" />
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-12 -mb-12" />

          <div className="relative">
            <div className="flex items-center justify-between mb-4">
              <span className="text-5xl">✨</span>
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
              </div>
            </div>
            <div className="text-sm font-medium text-orange-100 mb-1">Templates Generated</div>
            <div className="text-4xl font-bold mb-1">{stats?.templates_generated || 0}</div>
            <div className="text-xs text-orange-200">AI-powered previews</div>
          </div>
        </motion.div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div variants={itemVariants} className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <span className="text-2xl">⚡</span>
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Link href="/dashboard/scraping-jobs">
            <motion.div
              whileHover={{ scale: 1.02, boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)' }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center gap-4 p-6 border-2 border-gray-200 rounded-xl hover:border-blue-500 bg-gradient-to-br from-blue-50 to-purple-50 transition-all cursor-pointer group"
            >
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-2xl shadow-lg group-hover:shadow-xl transition-shadow">
                🔍
              </div>
              <div>
                <div className="font-bold text-gray-900 text-lg group-hover:text-blue-600 transition-colors">Start Scraping Job</div>
                <div className="text-sm text-gray-600">Discover new businesses</div>
              </div>
            </motion.div>
          </Link>

          <Link href="/dashboard/businesses">
            <motion.div
              whileHover={{ scale: 1.02, boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)' }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center gap-4 p-6 border-2 border-gray-200 rounded-xl hover:border-purple-500 bg-gradient-to-br from-purple-50 to-pink-50 transition-all cursor-pointer group"
            >
              <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center text-2xl shadow-lg group-hover:shadow-xl transition-shadow">
                📋
              </div>
              <div>
                <div className="font-bold text-gray-900 text-lg group-hover:text-purple-600 transition-colors">Browse Businesses</div>
                <div className="text-sm text-gray-600">View all discovered leads</div>
              </div>
            </motion.div>
          </Link>
        </div>
      </motion.div>

      {/* Getting Started */}
      <motion.div
        variants={itemVariants}
        className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl shadow-lg p-8 text-white relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-32 -mt-32" />
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full -ml-24 -mb-24" />

        <div className="relative">
          <h2 className="text-2xl font-bold mb-3 flex items-center gap-2">
            <span className="text-2xl">🚀</span>
            Getting Started
          </h2>
          <p className="text-blue-100 mb-6">
            Welcome to AutoWeb Outreach AI! Here's how to get started:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <motion.div
              whileHover={{ x: 4 }}
              className="flex items-start gap-3 bg-white/10 backdrop-blur-sm rounded-lg p-4"
            >
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0 font-bold">
                1
              </div>
              <div>
                <div className="font-semibold mb-1">Create a scraping job</div>
                <div className="text-sm text-blue-100">Discover UK businesses</div>
              </div>
            </motion.div>

            <motion.div
              whileHover={{ x: 4 }}
              className="flex items-start gap-3 bg-white/10 backdrop-blur-sm rounded-lg p-4"
            >
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0 font-bold">
                2
              </div>
              <div>
                <div className="font-semibold mb-1">Browse businesses</div>
                <div className="text-sm text-blue-100">Check their quality scores</div>
              </div>
            </motion.div>

            <motion.div
              whileHover={{ x: 4 }}
              className="flex items-start gap-3 bg-white/10 backdrop-blur-sm rounded-lg p-4"
            >
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0 font-bold">
                3
              </div>
              <div>
                <div className="font-semibold mb-1">View AI previews</div>
                <div className="text-sm text-blue-100">For low-scoring businesses</div>
              </div>
            </motion.div>

            <motion.div
              whileHover={{ x: 4 }}
              className="flex items-start gap-3 bg-white/10 backdrop-blur-sm rounded-lg p-4"
            >
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0 font-bold">
                4
              </div>
              <div>
                <div className="font-semibold mb-1">Start outreach</div>
                <div className="text-sm text-blue-100">Use previews in campaigns</div>
              </div>
            </motion.div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
