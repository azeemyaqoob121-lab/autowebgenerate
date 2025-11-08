'use client';

import { Business } from '@/lib/types';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useState } from 'react';
import TemplatePreviewModal from './TemplatePreviewModal';

interface BusinessCardProps {
  business: Business;
}

export default function BusinessCard({ business }: BusinessCardProps) {
  const [showPreview, setShowPreview] = useState(false);

  const getScoreColor = (score: number | null): string => {
    if (score === null) return 'bg-gray-500';
    if (score < 70) return 'bg-red-500';
    if (score < 85) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getScoreTextColor = (score: number | null): string => {
    if (score === null) return 'text-gray-700';
    if (score < 70) return 'text-red-700';
    if (score < 85) return 'text-yellow-700';
    return 'text-green-700';
  };

  return (
    <Link href={`/dashboard/businesses/${business.id}`}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(0, 0, 0, 0.12)' }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        className="bg-white rounded-2xl border border-gray-200 p-6 cursor-pointer hover:border-blue-400 transition-all overflow-hidden relative group"
      >
        {/* Gradient overlay on hover */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

        {/* Header with Name and Score */}
        <div className="flex items-start justify-between mb-4 relative">
          <div className="flex-1 min-w-0">
            <h3 className="text-xl font-bold text-gray-900 truncate mb-1 group-hover:text-blue-600 transition-colors">
              {business.name}
            </h3>
            {business.category && (
              <div className="flex items-center gap-1.5 mt-2">
                <span className="text-xs font-medium px-2.5 py-1 bg-gray-100 text-gray-700 rounded-full">
                  {business.category}
                </span>
              </div>
            )}
          </div>

          {/* Score Badge */}
          <div className="ml-4 flex-shrink-0">
            <motion.div
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ type: "spring", stiffness: 300 }}
              className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl shadow-lg ${getScoreColor(
                business.score
              )}`}
            >
              <span className="text-white font-bold text-lg">
                {business.score !== null ? Math.round(business.score) : 'N/A'}
              </span>
            </motion.div>
          </div>
        </div>

        {/* Description */}
        {business.description && (
          <div className="relative mb-4">
            <p className="text-sm text-gray-600 line-clamp-2">
              {business.description}
            </p>
          </div>
        )}

        {/* Contact Information */}
        <div className="space-y-2 mb-4 relative">
          {business.email && (
            <motion.div
              whileHover={{ x: 2 }}
              className="flex items-center gap-2.5 text-sm group/item"
            >
              <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center group-hover/item:bg-blue-100 transition-colors">
                <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <a
                href={`mailto:${business.email}`}
                className="text-blue-600 hover:text-blue-700 font-medium truncate"
                onClick={(e) => e.stopPropagation()}
              >
                {business.email}
              </a>
            </motion.div>
          )}

          {business.phone && (
            <motion.div
              whileHover={{ x: 2 }}
              className="flex items-center gap-2.5 text-sm group/item"
            >
              <div className="w-8 h-8 bg-green-50 rounded-lg flex items-center justify-center group-hover/item:bg-green-100 transition-colors">
                <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
              <a
                href={`tel:${business.phone}`}
                className="text-green-600 hover:text-green-700 font-medium"
                onClick={(e) => e.stopPropagation()}
              >
                {business.phone}
              </a>
            </motion.div>
          )}

          {business.location && (
            <motion.div
              whileHover={{ x: 2 }}
              className="flex items-center gap-2.5 text-sm group/item"
            >
              <div className="w-8 h-8 bg-purple-50 rounded-lg flex items-center justify-center group-hover/item:bg-purple-100 transition-colors">
                <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <span className="text-gray-700 font-medium truncate">{business.location}</span>
            </motion.div>
          )}
        </div>

        {/* Website Link */}
        {business.website_url && (
          <div className="pt-4 border-t border-gray-100 relative">
            <motion.a
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              href={business.website_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-sm font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all shadow-md hover:shadow-lg"
              onClick={(e) => e.stopPropagation()}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
              </svg>
              Visit Website
            </motion.a>
          </div>
        )}

        {/* AI Preview Button - Only for score < 70 (Qualified Leads) */}
        {business.score !== null && business.score < 70 && (
          <>
            <div className="mt-4 pt-4 border-t border-gray-100 relative">
              <motion.div
                whileHover={{ scale: 1.01 }}
                className="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-xl p-4 cursor-pointer"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setShowPreview(true);
                }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                      <span className="text-xl">✨</span>
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-purple-900">AI Preview</div>
                      <div className="text-xs text-purple-600">View improved design</div>
                    </div>
                  </div>
                  <motion.div
                    whileHover={{ x: 2 }}
                    className="text-purple-600"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </motion.div>
                </div>
              </motion.div>
            </div>

            {showPreview && (
              <TemplatePreviewModal
                businessId={business.id}
                businessName={business.name}
                onClose={() => setShowPreview(false)}
              />
            )}
          </>
        )}

        {/* High Quality Badge - Only for score >= 70 */}
        {business.score !== null && business.score >= 70 && (
          <div className="mt-4 pt-4 border-t border-gray-100 relative">
            <div className="flex items-center gap-2.5 bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="flex-1">
                <div className="text-xs font-semibold text-green-900">High Quality Website</div>
                <div className="text-xs text-green-600">Score: {Math.round(business.score)}%</div>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </Link>
  );
}
