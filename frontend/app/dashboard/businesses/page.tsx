'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import api from '@/lib/api';
import BusinessCard from '@/components/BusinessCard';
import type { Business, PaginatedBusinessResponse, BusinessDiscoveryResponse } from '@/lib/types';
import { motion } from 'framer-motion';

const ITEMS_PER_PAGE = 12;

function BusinessesContent() {
  const searchParams = useSearchParams();
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [discovering, setDiscovering] = useState(false);
  const [error, setError] = useState('');
  const [discoveryStats, setDiscoveryStats] = useState<BusinessDiscoveryResponse | null>(null);
  const [polling, setPolling] = useState(false);

  // Filter states
  const [locationFilter, setLocationFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  // Default to showing ONLY qualified leads (score < 70)
  const [showAllScores, setShowAllScores] = useState(false);

  // Applied filters (only set when Search button is clicked)
  const [appliedLocation, setAppliedLocation] = useState('');
  const [appliedCategory, setAppliedCategory] = useState('');

  // Check URL parameters on mount to set initial state
  useEffect(() => {
    const showAll = searchParams.get('showAll');
    if (showAll === 'true') {
      // If showAll=true is in URL (from dashboard Total Businesses card),
      // check "Show all scores" to show ALL businesses
      setShowAllScores(true);
    }
  }, [searchParams]);

  useEffect(() => {
    fetchBusinesses();
  }, [currentPage, appliedLocation, appliedCategory, showAllScores]);

  const fetchBusinesses = async () => {
    setLoading(true);
    setError('');

    try {
      const params: any = {
        limit: ITEMS_PER_PAGE,
        offset: (currentPage - 1) * ITEMS_PER_PAGE,
      };

      // Only apply score filter if not showing all scores
      if (!showAllScores) {
        params.score_max = 69; // Only show businesses with score < 70 (qualified leads!)
      }

      // Add filters from applied state
      if (appliedLocation.trim()) {
        params.location = appliedLocation.trim();
      }

      if (appliedCategory.trim()) {
        params.category = appliedCategory.trim();
      }

      const response: PaginatedBusinessResponse = await api.getBusinesses(params);
      setBusinesses(response.items);
      setTotal(response.total);
    } catch (err: any) {
      console.error('Failed to fetch businesses:', err);
      setError('Failed to load businesses. Please try again.');
      setBusinesses([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const handleDiscoverBusinesses = async () => {
    if (!locationFilter.trim() || !categoryFilter.trim()) {
      setError('Please enter both location and category to discover businesses');
      return;
    }

    setDiscovering(true);
    setError('');
    setDiscoveryStats(null);

    try {
      console.log('Discovering businesses...', {
        location: locationFilter.trim(),
        category: categoryFilter.trim(),
      });

      const response: BusinessDiscoveryResponse = await api.discoverBusinesses({
        location: locationFilter.trim(),
        category: categoryFilter.trim(),
        max_results: 10, // Search businesses and keep those with score < 70
        auto_evaluate: true, // Automatically evaluate and generate templates
      });

      console.log('Discovery response:', response);

      setDiscoveryStats(response);

      // ALWAYS fetch from database after discovery to ensure we get ALL saved businesses
      // The discovery response may be filtered, but database has all businesses
      if (response.saved > 0) {
        console.log(`Discovery saved ${response.saved} businesses, fetching all from database...`);

        try {
          const params: any = {
            limit: ITEMS_PER_PAGE,
            offset: 0,
            location: locationFilter.trim(),
            category: categoryFilter.trim(),
          };

          const fetchedResponse = await api.getBusinesses(params);
          console.log(`Fetched ${fetchedResponse.items.length} businesses from database`);
          setBusinesses(fetchedResponse.items);
          setTotal(fetchedResponse.total);
        } catch (fetchErr) {
          console.error('Failed to fetch businesses after discovery:', fetchErr);
          // Fallback to discovery response if database fetch fails
          setBusinesses(response.businesses || []);
          setTotal(response.businesses?.length || 0);
        }
      } else {
        // No businesses were saved (all had score >= 70 or discovery failed)
        console.log('No businesses saved from discovery');
        setBusinesses([]);
        setTotal(0);
      }

      setAppliedLocation(locationFilter);
      setAppliedCategory(categoryFilter);
      setCurrentPage(1);

      // Turn off discovering and polling flags on success
      setDiscovering(false);
      setPolling(false);
      setError(''); // Clear any previous errors
    } catch (err: any) {
      console.error('Failed to discover businesses:', err);

      // If timeout, the backend is still processing - poll for results
      if (err.code === 'ECONNABORTED' || err.message.includes('timeout')) {
        console.log('Request timeout - backend is still processing, will poll for results');

        // Poll for businesses every 5 seconds
        let attempts = 0;
        const maxAttempts = 10;

        const pollForBusinesses = async () => {
          attempts++;
          console.log(`Checking for businesses... (${attempts}/${maxAttempts})`);
          setPolling(true);

          try {
            const params: any = {
              limit: ITEMS_PER_PAGE,
              offset: 0,
              location: locationFilter.trim(),
              category: categoryFilter.trim(),
            };

            const response: PaginatedBusinessResponse = await api.getBusinesses(params);

            if (response.items.length > 0) {
              console.log(`Found ${response.items.length} businesses!`);
              setBusinesses(response.items);
              setTotal(response.total);
              setAppliedLocation(locationFilter);
              setAppliedCategory(categoryFilter);
              setCurrentPage(1);
              setError(''); // Clear any errors
              setPolling(false);
              setDiscovering(false);
            } else if (attempts < maxAttempts) {
              setTimeout(pollForBusinesses, 5000);
            } else {
              setError('No businesses found. Try different search terms.');
              setPolling(false);
              setDiscovering(false);
            }
          } catch (pollErr) {
            console.error('Error checking for businesses:', pollErr);
            if (attempts < maxAttempts) {
              setTimeout(pollForBusinesses, 5000);
            } else {
              setError('Unable to fetch businesses. Please try again.');
              setPolling(false);
              setDiscovering(false);
            }
          }
        };

        setTimeout(pollForBusinesses, 5000);
      } else {
        setError('Failed to discover businesses. Please try again.');
        setDiscovering(false);
      }
    }
  };

  const handleClearFilters = () => {
    setLocationFilter('');
    setCategoryFilter('');
    setAppliedLocation('');
    setAppliedCategory('');
    setCurrentPage(1);
    setDiscoveryStats(null);
  };

  const totalPages = Math.ceil(total / ITEMS_PER_PAGE);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Render loading skeleton
  if (loading && !discovering) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">
          {showAllScores ? (
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              All Businesses
            </span>
          ) : (
            <span className="bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
              Qualified Leads (Score &lt; 70)
            </span>
          )}
        </h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <div
              key={i}
              className="bg-white rounded-lg border border-gray-200 p-6 animate-pulse"
            >
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 rounded"></div>
                <div className="h-3 bg-gray-200 rounded w-5/6"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Render error state
  if (error && !discovering) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">
          {showAllScores ? (
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              All Businesses
            </span>
          ) : (
            <span className="bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
              Qualified Leads (Score &lt; 70)
            </span>
          )}
        </h1>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-600">{error}</p>
          <button
            onClick={fetchBusinesses}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Render empty state
  if (businesses.length === 0 && !discovering) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">
            {showAllScores ? (
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                All Businesses
              </span>
            ) : (
              <span className="bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                Find Qualified Leads (Score &lt; 70)
              </span>
            )}
          </h1>

          {/* Checkbox to toggle all scores */}
          <div className="flex items-center gap-3 bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showAllScores}
                onChange={(e) => {
                  setShowAllScores(e.target.checked);
                  setCurrentPage(1);
                }}
                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
              />
              <span className="text-sm font-medium text-gray-700">
                Show all scores
              </span>
            </label>
            <div className="text-xs text-gray-500 border-l border-gray-300 pl-3">
              {showAllScores ? (
                <span className="text-blue-600 font-medium">✓ Viewing all businesses</span>
              ) : (
                <span className="text-orange-600 font-medium">🎯 Viewing score &lt; 70 only</span>
              )}
            </div>
          </div>
        </div>

        {/* Search Section */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
                UK Location
              </label>
              <input
                id="location"
                type="text"
                placeholder="e.g., London, Manchester, Birmingham..."
                value={locationFilter}
                onChange={(e) => setLocationFilter(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleDiscoverBusinesses();
                  }
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white"
              />
            </div>

            <div className="flex-1">
              <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
                Business Category / Niche
              </label>
              <input
                id="category"
                type="text"
                placeholder="e.g., Plumber, Restaurant, Electrician..."
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleDiscoverBusinesses();
                  }
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white"
              />
            </div>

            <div className="flex items-end">
              <button
                onClick={handleDiscoverBusinesses}
                disabled={!locationFilter.trim() || !categoryFilter.trim()}
                className="px-8 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-md text-sm font-medium hover:from-blue-700 hover:to-indigo-700 transition whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
              >
                🔍 Discover Businesses
              </button>
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-600 bg-white bg-opacity-60 rounded-md p-3">
            <p className="font-medium text-gray-800 mb-1">✨ Smart Discovery Features:</p>
            <ul className="list-disc list-inside space-y-1 text-gray-700">
              <li>Searches UK businesses from Google Places (up to 10 businesses)</li>
              <li>Evaluates EVERY business using Google Lighthouse (~30-60 seconds each)</li>
              <li><strong>💾 Stores ALL businesses</strong> in database for future reference</li>
              <li><strong>🎯 Shows ONLY businesses with score &lt; 70</strong> (your best leads!)</li>
              <li>Generates AI templates for low-scoring businesses using GPT-4</li>
              <li><strong>⏱️ Total time: 3-7 minutes</strong> - Finding qualified leads!</li>
            </ul>
          </div>
        </div>

        <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
          <span className="text-6xl mb-4 block">{showAllScores ? '📊' : '🎯'}</span>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {showAllScores ? 'No businesses in database yet' : 'No qualified leads yet'}
          </h3>
          <p className="text-gray-500">
            {showAllScores
              ? 'Enter a location and category above to discover businesses from Google Places!'
              : 'Enter a location and category above to discover businesses with website scores < 70!'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            {showAllScores ? (
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                All Businesses
              </span>
            ) : (
              <span className="bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                Qualified Leads (Score &lt; 70)
              </span>
            )}
          </h1>
          <p className="text-sm font-medium text-gray-700 mt-2">
            Showing {(currentPage - 1) * ITEMS_PER_PAGE + 1} -{' '}
            {Math.min(currentPage * ITEMS_PER_PAGE, total)} of <span className="font-bold text-blue-600">{total}</span> businesses
            {!showAllScores && ' that need website improvement'}
          </p>
        </div>

        {/* Checkbox to toggle all scores */}
        <div className="flex items-center gap-3 bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showAllScores}
              onChange={(e) => {
                setShowAllScores(e.target.checked);
                setCurrentPage(1); // Reset to first page when toggling
              }}
              className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
            />
            <span className="text-sm font-medium text-gray-700">
              Show all scores
            </span>
          </label>
          <div className="text-xs text-gray-500 border-l border-gray-300 pl-3">
            {showAllScores ? (
              <span className="text-blue-600 font-medium">✓ Viewing all businesses</span>
            ) : (
              <span className="text-orange-600 font-medium">🎯 Viewing score &lt; 70 only</span>
            )}
          </div>
        </div>
      </div>

      {/* Discovery Stats */}
      {discoveryStats && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">✅</span>
            <h3 className="text-lg font-semibold text-green-800">Discovery Complete!</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="bg-white bg-opacity-60 rounded-md p-3">
              <p className="text-gray-600">Found</p>
              <p className="text-2xl font-bold text-gray-900">{discoveryStats.discovered}</p>
            </div>
            <div className="bg-white bg-opacity-60 rounded-md p-3">
              <p className="text-gray-600">Saved</p>
              <p className="text-2xl font-bold text-blue-600">{discoveryStats.saved}</p>
            </div>
            <div className="bg-white bg-opacity-60 rounded-md p-3">
              <p className="text-gray-600">Evaluated</p>
              <p className="text-2xl font-bold text-indigo-600">{discoveryStats.evaluated}</p>
            </div>
            <div className="bg-white bg-opacity-60 rounded-md p-3">
              <p className="text-gray-600">Templates Generated</p>
              <p className="text-2xl font-bold text-purple-600">{discoveryStats.templates_generated}</p>
            </div>
          </div>
        </div>
      )}

      {/* Search Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
              UK Location
            </label>
            <input
              id="location"
              type="text"
              placeholder="e.g., London, Manchester..."
              value={locationFilter}
              onChange={(e) => setLocationFilter(e.target.value)}
              disabled={discovering}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleDiscoverBusinesses();
                }
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 text-gray-900 bg-white"
            />
          </div>

          <div className="flex-1">
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
              Category / Niche
            </label>
            <input
              id="category"
              type="text"
              placeholder="e.g., Plumbing, Restaurant..."
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              disabled={discovering}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleDiscoverBusinesses();
                }
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 text-gray-900 bg-white"
            />
          </div>

          <div className="flex items-end gap-2">
            <button
              onClick={handleDiscoverBusinesses}
              disabled={discovering || !locationFilter.trim() || !categoryFilter.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {discovering ? (
                <>
                  <span className="inline-block animate-spin mr-2">⚙️</span>
                  Discovering...
                </>
              ) : (
                '🔍 Discover More'
              )}
            </button>
            <button
              onClick={handleClearFilters}
              disabled={discovering}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition whitespace-nowrap disabled:opacity-50"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Active Filters Display */}
        {(appliedLocation || appliedCategory) && (
          <div className="mt-4 flex items-center gap-2 flex-wrap">
            <span className="text-sm text-gray-600">Active filters:</span>
            {appliedLocation && (
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                Location: {appliedLocation}
              </span>
            )}
            {appliedCategory && (
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                Category: {appliedCategory}
              </span>
            )}
          </div>
        )}

        {/* Discovering indicator */}
        {discovering && (
          <div className="mt-4 bg-blue-50 border border-blue-200 rounded-md p-4">
            <div className="flex items-center gap-3">
              <div className="animate-spin text-2xl">⚙️</div>
              <div className="flex-1">
                <p className="font-medium text-blue-900">🔍 Smart Discovery in Progress...</p>
                <p className="text-sm text-blue-700 mt-1">
                  <strong>Step 1:</strong> Finding ALL available businesses on Google Places<br />
                  <strong>Step 2:</strong> Evaluating EVERY business with Lighthouse (~30-60 seconds each)<br />
                  <strong>Step 3:</strong> Storing ALL businesses in database<br />
                  <strong>Step 4:</strong> Filtering businesses with score &lt; 70 (your best leads!)<br />
                  <strong>Step 5:</strong> Generating AI templates for qualified leads<br />
                  <strong>Step 6:</strong> Loading results (will appear automatically)
                </p>
                <div className="mt-2 bg-yellow-50 border border-yellow-200 rounded-md p-2">
                  <p className="text-xs text-yellow-800 font-medium">
                    ⏱️ This takes 3-7 minutes. Evaluating all businesses and filtering the best leads. Do not refresh!
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Polling indicator */}
        {polling && (
          <div className="mt-4 bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex items-center gap-3">
              <div className="animate-spin text-2xl">🔄</div>
              <div className="flex-1">
                <p className="font-medium text-green-900">✅ Discovery complete! Loading your businesses...</p>
                <p className="text-sm text-green-700 mt-1">
                  Checking for saved businesses. Results will appear in a few seconds.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Business Card Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {businesses.map((business) => (
          <BusinessCard key={business.id} business={business} />
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 pt-8 pb-4">
          {/* Previous Button */}
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg text-sm font-semibold hover:from-blue-700 hover:to-blue-800 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg disabled:shadow-none"
          >
            ← Previous
          </button>

          {/* Page Numbers */}
          <div className="flex items-center gap-2">
            {[...Array(totalPages)].map((_, i) => {
              const page = i + 1;
              // Show first page, last page, current page, and 2 pages around current
              const showPage =
                page === 1 ||
                page === totalPages ||
                (page >= currentPage - 1 && page <= currentPage + 1);

              if (!showPage && page === 2) {
                return (
                  <span key={page} className="px-2 text-gray-500 font-bold">
                    ...
                  </span>
                );
              }

              if (!showPage && page === totalPages - 1) {
                return (
                  <span key={page} className="px-2 text-gray-500 font-bold">
                    ...
                  </span>
                );
              }

              if (!showPage) return null;

              return (
                <button
                  key={page}
                  onClick={() => handlePageChange(page)}
                  className={`min-w-[44px] px-4 py-3 rounded-lg text-sm font-bold transition-all shadow-md ${
                    currentPage === page
                      ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white border-2 border-orange-600 scale-110 shadow-lg'
                      : 'bg-white text-gray-700 border-2 border-gray-300 hover:border-blue-500 hover:bg-blue-50 hover:text-blue-700 hover:scale-105'
                  }`}
                >
                  {page}
                </button>
              );
            })}
          </div>

          {/* Next Button */}
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg text-sm font-semibold hover:from-blue-700 hover:to-blue-800 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg disabled:shadow-none"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}

export default function BusinessesPage() {
  return (
    <Suspense fallback={
      <div className="space-y-6">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Loading Businesses...
        </h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <div
              key={i}
              className="bg-white rounded-lg border border-gray-200 p-6 animate-pulse"
            >
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 rounded"></div>
                <div className="h-3 bg-gray-200 rounded w-5/6"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    }>
      <BusinessesContent />
    </Suspense>
  );
}
