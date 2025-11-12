'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import api from '@/lib/api';
import type { Business, Evaluation, Template } from '@/lib/types';
import Link from 'next/link';

export default function BusinessDetailPage() {
  const params = useParams();
  const router = useRouter();
  const businessId = params?.id as string;

  const [business, setBusiness] = useState<Business | null>(null);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [evaluating, setEvaluating] = useState(false);
  const [loadingTemplates, setLoadingTemplates] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);
  const [fullscreenTemplate, setFullscreenTemplate] = useState<number | null>(null);

  useEffect(() => {
    if (businessId) {
      fetchBusinessDetails();
    }
  }, [businessId]);

  const fetchBusinessDetails = async () => {
    setLoading(true);
    setError('');

    try {
      const businessData = await api.getBusiness(businessId);
      setBusiness(businessData);

      // Try to fetch evaluation (may not exist)
      try {
        const evaluationData = await api.getBusinessEvaluation(businessId);
        setEvaluation(evaluationData);
      } catch (evalErr) {
        // Evaluation doesn't exist yet
        setEvaluation(null);
      }
    } catch (err: any) {
      console.error('Failed to fetch business:', err);
      setError('Business not found');
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluate = async () => {
    if (!businessId) return;

    setEvaluating(true);
    try {
      const evaluationData = await api.triggerEvaluation(businessId);
      setEvaluation(evaluationData);

      // Refresh business data to update score
      const businessData = await api.getBusiness(businessId);
      setBusiness(businessData);
    } catch (err: any) {
      console.error('Failed to evaluate business:', err);
      alert('Failed to evaluate website. Please try again.');
    } finally {
      setEvaluating(false);
    }
  };

  const handleViewTemplates = async () => {
    if (!businessId) return;

    setLoadingTemplates(true);
    try {
      // Try to get existing templates first
      let templatesData = await api.getBusinessTemplates(businessId);

      // If no templates exist, generate them
      if (templatesData.length === 0) {
        templatesData = await api.generateTemplates(businessId, 3);
      }

      setTemplates(templatesData);
      setShowTemplates(true);
    } catch (err: any) {
      console.error('Failed to load templates:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to load templates. Please try again.';
      alert(errorMsg);
    } finally {
      setLoadingTemplates(false);
    }
  };

  const handleRegenerateTemplates = async () => {
    if (!businessId) return;

    setLoadingTemplates(true);
    try {
      const templatesData = await api.regenerateTemplates(businessId, 3);
      setTemplates(templatesData);
    } catch (err: any) {
      console.error('Failed to regenerate templates:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to regenerate templates. Please try again.';
      alert(errorMsg);
    } finally {
      setLoadingTemplates(false);
    }
  };

  const getScoreColor = (score: number | null): string => {
    if (score === null) return 'text-gray-500';
    if (score < 70) return 'text-red-500';
    if (score < 85) return 'text-yellow-500';
    return 'text-green-500';
  };

  const openTemplateInNewTab = (template: Template) => {
    const blob = new Blob([template.html_content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading business details...</div>
      </div>
    );
  }

  if (error || !business) {
    return (
      <div className="space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-600">{error || 'Business not found'}</p>
          <Link
            href="/dashboard/businesses"
            className="mt-4 inline-block px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
          >
            Back to Businesses
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <nav className="text-sm">
        <Link
          href="/dashboard/businesses"
          className="text-blue-600 hover:underline"
        >
          ← Back to Businesses
        </Link>
      </nav>

      {/* Business Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6">
        <div className="flex flex-col sm:flex-row items-start sm:justify-between gap-4">
          <div className="flex-1">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
              {business.name}
            </h1>
            {business.category && (
              <p className="text-base sm:text-lg text-gray-600">{business.category}</p>
            )}
            {business.location && (
              <p className="text-sm text-gray-500 mt-1">📍 {business.location}</p>
            )}
          </div>

          {/* Score Badge */}
          {business.score !== null && (
            <div className="text-center sm:text-right">
              <div
                className={`text-4xl sm:text-5xl md:text-6xl font-bold ${getScoreColor(business.score)}`}
              >
                {Math.round(business.score)}
              </div>
              <div className="text-xs sm:text-sm text-gray-500 mt-1">Quality Score</div>
            </div>
          )}
        </div>

        {/* Description */}
        {business.description && (
          <p className="text-gray-700 mt-6">{business.description}</p>
        )}
      </div>

      {/* Contact Information */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6">
        <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4">
          Contact Information
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {business.email && (
            <div>
              <div className="text-sm text-gray-500 mb-1">Email</div>
              <a
                href={`mailto:${business.email}`}
                className="text-blue-600 hover:underline"
              >
                {business.email}
              </a>
            </div>
          )}

          {business.phone && (
            <div>
              <div className="text-sm text-gray-500 mb-1">Phone</div>
              <a
                href={`tel:${business.phone}`}
                className="text-blue-600 hover:underline"
              >
                {business.phone}
              </a>
            </div>
          )}

          {business.address && (
            <div>
              <div className="text-sm text-gray-500 mb-1">Address</div>
              <p className="text-gray-900">{business.address}</p>
            </div>
          )}

          {business.website_url && (
            <div>
              <div className="text-sm text-gray-500 mb-1">Website</div>
              <a
                href={business.website_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline inline-flex items-center gap-1"
              >
                Visit Website →
              </a>
            </div>
          )}
        </div>
      </div>

      {/* Evaluation Details */}
      {evaluation && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Website Evaluation
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {evaluation.performance_score !== null && (
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">
                  {Math.round(evaluation.performance_score * 100)}
                </div>
                <div className="text-sm text-gray-600 mt-1">Performance</div>
              </div>
            )}

            {evaluation.seo_score !== null && (
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">
                  {Math.round(evaluation.seo_score * 100)}
                </div>
                <div className="text-sm text-gray-600 mt-1">SEO</div>
              </div>
            )}

            {evaluation.accessibility_score !== null && (
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">
                  {Math.round(evaluation.accessibility_score * 100)}
                </div>
                <div className="text-sm text-gray-600 mt-1">Accessibility</div>
              </div>
            )}

            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className={`text-2xl font-bold ${getScoreColor(evaluation.aggregate_score)}`}>
                {Math.round(evaluation.aggregate_score)}
              </div>
              <div className="text-sm text-gray-600 mt-1">Aggregate</div>
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-500">
            Evaluated on {new Date(evaluation.evaluated_at).toLocaleDateString()}
          </div>
        </div>
      )}

      {/* No Evaluation */}
      {!evaluation && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
          <p className="text-gray-600 mb-4">
            This business hasn't been evaluated yet.
          </p>
          <button
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handleEvaluate}
            disabled={evaluating}
          >
            {evaluating ? 'Evaluating...' : 'Evaluate Website'}
          </button>
        </div>
      )}

      {/* AI Preview / Templates Section - Only for score < 70 (Qualified Leads) */}
      {business.score !== null && business.score < 70 && (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <span className="text-2xl">🎨</span>
            <div className="flex-1">
              <h3 className="font-semibold text-purple-900 mb-1">
                AI-Generated Website Preview Available
              </h3>
              <p className="text-sm text-purple-700 mb-4">
                This business has improvement opportunities (score {Math.round(business.score)}%).
                View AI-generated preview websites that show how their site could be improved with modern design and best practices.
              </p>
              <button
                className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={handleViewTemplates}
                disabled={loadingTemplates}
              >
                {loadingTemplates ? 'Generating Preview...' : 'View AI-Generated Website Preview'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Qualified Lead Badge - Only for score < 70 */}
      {business.score !== null && business.score < 70 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <span className="text-2xl">🎯</span>
            <div>
              <h3 className="font-semibold text-red-900 mb-1">
                Qualified Lead Opportunity
              </h3>
              <p className="text-sm text-red-700">
                This business has a quality score below 70%, making it a prime
                candidate for website improvement services. Consider reaching out
                with a customized proposal.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Templates Modal */}
      {showTemplates && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  AI-Generated Templates
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  {templates.length} template{templates.length !== 1 ? 's' : ''} available
                </p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={handleRegenerateTemplates}
                  disabled={loadingTemplates}
                  className="px-4 py-2 border border-purple-300 text-purple-700 rounded-md hover:bg-purple-50 transition text-sm font-medium disabled:opacity-50"
                >
                  {loadingTemplates ? 'Regenerating...' : 'Regenerate Templates'}
                </button>
                <button
                  onClick={() => setShowTemplates(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              {templates.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-600 mb-4">
                    No templates available yet. Click "Regenerate Templates" to create them.
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  {templates.map((template, index) => (
                    <div
                      key={template.id}
                      className="border border-gray-200 rounded-lg overflow-hidden"
                    >
                      {/* Template Header */}
                      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                        <div className="flex items-center justify-between">
                          <h3 className="font-semibold text-gray-900">
                            Template Variant #{template.variant_number}
                          </h3>
                          <span className="text-xs text-gray-500">
                            Generated: {new Date(template.generated_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>

                      {/* Improvements */}
                      {template.improvements_made && template.improvements_made.length > 0 && (
                        <div className="px-4 py-3 bg-blue-50 border-b border-gray-200">
                          <h4 className="text-sm font-medium text-gray-900 mb-2">
                            Improvements Made:
                          </h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {template.improvements_made.map((improvement, idx) => (
                              <div
                                key={idx}
                                className="flex items-start gap-2 text-sm"
                              >
                                <span
                                  className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                                    improvement.impact === 'high'
                                      ? 'bg-red-100 text-red-700'
                                      : improvement.impact === 'medium'
                                      ? 'bg-yellow-100 text-yellow-700'
                                      : 'bg-green-100 text-green-700'
                                  }`}
                                >
                                  {improvement.category}
                                </span>
                                <span className="text-gray-700 flex-1">
                                  {improvement.description}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Template Preview */}
                      <div className="p-4">
                        <div className="bg-gray-100 rounded border border-gray-300 overflow-hidden relative">
                          <iframe
                            srcDoc={template.html_content}
                            className="w-full bg-white"
                            style={{ height: fullscreenTemplate === index ? '90vh' : '600px' }}
                            title={`Template ${template.variant_number}`}
                            sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                          />
                          <button
                            onClick={() => setFullscreenTemplate(fullscreenTemplate === index ? null : index)}
                            className="absolute top-2 right-2 p-2 bg-white/90 hover:bg-white rounded-lg shadow-md transition-colors"
                            title={fullscreenTemplate === index ? "Exit fullscreen" : "Enter fullscreen"}
                          >
                            {fullscreenTemplate === index ? (
                              <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
                              </svg>
                            ) : (
                              <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" />
                              </svg>
                            )}
                          </button>
                        </div>
                        <div className="mt-3 flex gap-2">
                          <button
                            onClick={() => openTemplateInNewTab(template)}
                            className="px-3 py-1.5 bg-purple-600 text-white text-sm rounded hover:bg-purple-700 transition flex items-center gap-2"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                            Open in Browser
                          </button>
                          <a
                            href={`data:text/html;charset=utf-8,${encodeURIComponent(
                              template.html_content
                            )}`}
                            download={`template-${template.variant_number}.html`}
                            className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition"
                          >
                            Download HTML
                          </a>
                          {template.css_content && (
                            <a
                              href={`data:text/css;charset=utf-8,${encodeURIComponent(
                                template.css_content
                              )}`}
                              download={`template-${template.variant_number}.css`}
                              className="px-3 py-1.5 border border-gray-300 text-gray-700 text-sm rounded hover:bg-gray-50 transition"
                            >
                              Download CSS
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
