'use client';

export default function ScrapingJobsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Scraping Jobs</h1>
        <p className="text-sm text-gray-500 mt-1">
          Manage your business discovery scraping jobs
        </p>
      </div>

      {/* Coming Soon Message */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-12 text-center">
        <span className="text-6xl mb-4 block">🔍</span>
        <h2 className="text-2xl font-semibold text-blue-900 mb-2">
          Scraping Jobs Coming Soon
        </h2>
        <p className="text-blue-700 mb-6 max-w-2xl mx-auto">
          The scraping functionality will be implemented in Epic 2. This feature
          will allow you to automatically discover UK businesses from Checkatrade,
          Yell, and other business directories.
        </p>

        <div className="bg-white rounded-lg p-6 max-w-2xl mx-auto text-left">
          <h3 className="font-semibold text-gray-900 mb-3">Upcoming Features:</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">✓</span>
              <span>Automated scraping from Checkatrade and Yell.com</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">✓</span>
              <span>Filter by location and business category</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">✓</span>
              <span>Real-time progress tracking</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">✓</span>
              <span>Automatic data validation and deduplication</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">✓</span>
              <span>Background processing with Celery</span>
            </li>
          </ul>
        </div>

        <div className="mt-8 text-sm text-gray-500">
          For now, you can manually add businesses or use the test data seeded in
          the database.
        </div>
      </div>
    </div>
  );
}
