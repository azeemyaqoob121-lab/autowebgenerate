'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '@/lib/api';
import { Template } from '@/lib/types';

interface TemplatePreviewModalProps {
  businessId: string;
  businessName: string;
  onClose: () => void;
}

export default function TemplatePreviewModal({
  businessId,
  businessName,
  onClose,
}: TemplatePreviewModalProps) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [generating, setGenerating] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, [businessId]);

  const loadTemplates = async () => {
    setLoading(true);
    setError('');
    try {
      const templatesData = await api.getBusinessTemplates(businessId);

      if (templatesData && templatesData.length > 0) {
        setTemplates(templatesData);
        setSelectedTemplate(templatesData[0]);
      } else {
        // No templates exist, generate them
        await generateTemplates();
      }
    } catch (err: any) {
      console.error('Failed to load templates:', err);
      setError(err.message || 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const generateTemplates = async () => {
    setGenerating(true);
    setError('');
    try {
      const templatesData = await api.generateTemplates(businessId, 1); // Generate 1 variant
      if (templatesData && templatesData.length > 0) {
        setTemplates(templatesData);
        setSelectedTemplate(templatesData[0]);
      }
    } catch (err: any) {
      console.error('Failed to generate templates:', err);
      setError(err.message || 'Failed to generate AI templates. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const openInNewTab = () => {
    if (!selectedTemplate) return;

    const isCompleteHTML = selectedTemplate.html_content &&
                          (selectedTemplate.html_content.includes('<!DOCTYPE html>') ||
                           selectedTemplate.html_content.includes('<html'));

    let fullHTML;
    if (isCompleteHTML) {
      fullHTML = selectedTemplate.html_content;
    } else {
      fullHTML = `
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>${businessName} - AI Preview</title>
          <style>${selectedTemplate.css_content || ''}</style>
        </head>
        <body>
          ${selectedTemplate.html_content || '<p>No template content available</p>'}
        </body>
        </html>
      `;
    }

    const blob = new Blob([fullHTML], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  const renderTemplatePreview = () => {
    if (!selectedTemplate) return null;

    // Check if html_content is already a complete HTML document
    const isCompleteHTML = selectedTemplate.html_content &&
                          (selectedTemplate.html_content.includes('<!DOCTYPE html>') ||
                           selectedTemplate.html_content.includes('<html'));

    let fullHTML;

    if (isCompleteHTML) {
      // Use the complete HTML document as-is (CSS and JS already inline)
      fullHTML = selectedTemplate.html_content;
    } else {
      // Legacy: Combine separate parts for old templates
      fullHTML = `
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>${businessName} - AI Preview</title>
          <style>${selectedTemplate.css_content || ''}</style>
        </head>
        <body>
          ${selectedTemplate.html_content || '<p>No template content available</p>'}
        </body>
        </html>
      `;
    }

    return (
      <iframe
        srcDoc={fullHTML}
        title="Template Preview"
        className="w-full h-full border-0"
        sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
        style={{ minHeight: isFullscreen ? '100vh' : '600px' }}
      />
    );
  };

  return (
    <AnimatePresence>
      <div className={`fixed inset-0 z-50 flex items-center justify-center ${isFullscreen ? 'p-0' : 'p-4'}`} onClick={isFullscreen ? undefined : onClose}>
        {/* Backdrop */}
        {!isFullscreen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          />
        )}

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.2 }}
          className={`relative bg-white shadow-2xl w-full flex flex-col overflow-hidden ${
            isFullscreen
              ? 'h-screen max-w-none rounded-none'
              : 'max-w-6xl max-h-[90vh] rounded-2xl'
          }`}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200 bg-gradient-to-r from-purple-50 to-pink-50">
            <div className="flex items-center gap-2 sm:gap-3 min-w-0">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-lg sm:text-xl">✨</span>
              </div>
              <div className="min-w-0">
                <h2 className="text-base sm:text-xl font-bold text-gray-900 truncate">AI Website Preview</h2>
                <p className="text-xs sm:text-sm text-gray-600 truncate">{businessName}</p>
              </div>
            </div>

            <div className="flex items-center gap-1 sm:gap-2">
              <button
                onClick={() => setIsFullscreen(!isFullscreen)}
                className="p-1.5 sm:p-2 hover:bg-white/50 rounded-lg transition-colors"
                aria-label={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
                title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
              >
                {isFullscreen ? (
                  <svg className="w-5 h-5 sm:w-6 sm:h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 sm:w-6 sm:h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" />
                  </svg>
                )}
              </button>
              <button
                onClick={openInNewTab}
                className="p-1.5 sm:p-2 hover:bg-white/50 rounded-lg transition-colors"
                aria-label="Open in new tab"
                title="Open in new tab"
              >
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </button>
              <button
                onClick={onClose}
                className="p-1.5 sm:p-2 hover:bg-white/50 rounded-lg transition-colors"
                aria-label="Close modal"
              >
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Template Selector (if multiple templates) */}
          {templates.length > 1 && (
            <div className="px-6 py-3 border-b border-gray-200 bg-gray-50">
              <div className="flex gap-2">
                {templates.map((template, index) => (
                  <button
                    key={template.id}
                    onClick={() => setSelectedTemplate(template)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      selectedTemplate?.id === template.id
                        ? 'bg-purple-500 text-white shadow-lg'
                        : 'bg-white text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    Variant {template.variant_number || index + 1}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Content */}
          <div className="flex-1 overflow-hidden bg-gray-100">
            {loading || generating ? (
              <div className="flex flex-col items-center justify-center h-full gap-4">
                <div className="w-16 h-16 border-4 border-purple-200 border-t-purple-500 rounded-full animate-spin" />
                <p className="text-lg font-medium text-gray-700">
                  {generating ? 'Generating AI template with GPT-4...' : 'Loading preview...'}
                </p>
                <p className="text-sm text-gray-500">This may take 10-30 seconds</p>
              </div>
            ) : error ? (
              <div className="flex flex-col items-center justify-center h-full gap-4 p-6">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <p className="text-lg font-medium text-gray-700">Failed to load template</p>
                <p className="text-sm text-gray-500 text-center max-w-md">{error}</p>
                <button
                  onClick={generateTemplates}
                  className="mt-4 px-6 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
                >
                  Try Again
                </button>
              </div>
            ) : (
              renderTemplatePreview()
            )}
          </div>

          {/* Footer */}
          {selectedTemplate && !loading && !error && (
            <div className="px-6 py-4 border-t border-gray-200 bg-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>AI-generated professional design</span>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={loadTemplates}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    Refresh
                  </button>
                  <button
                    onClick={onClose}
                    className="px-6 py-2 text-sm font-medium text-white bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-lg transition-all shadow-md hover:shadow-lg"
                  >
                    Close Preview
                  </button>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
