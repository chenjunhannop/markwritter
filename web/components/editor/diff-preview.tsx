/**
 * DiffPreview Component for WRT-005-V1
 *
 * Displays a simple diff preview showing original vs modified content.
 * For V1, we use a side-by-side comparison view.
 * V2 will implement inline word-level diff with diff-match-patch.
 */

import React from 'react';

interface DiffPreviewProps {
  original: string;
  modified: string;
  onAccept: () => void;
  onReject: () => void;
}

export function DiffPreview({
  original,
  modified,
  onAccept,
  onReject,
}: DiffPreviewProps) {
  const isDifferent = original.trim() !== modified.trim();

  return (
    <div className="border rounded-lg overflow-hidden bg-white dark:bg-gray-800">
      {/* Header */}
      <div className="bg-gray-50 dark:bg-gray-700 px-4 py-2 border-b dark:border-gray-600">
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-200">
          AI 修改预览
        </h3>
      </div>

      {/* Content */}
      <div className="grid grid-cols-2 divide-x dark:divide-gray-600">
        {/* Original */}
        <div className="p-4">
          <div className="text-xs font-medium text-red-600 dark:text-red-400 mb-2">
            原文
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-300 whitespace-pre-wrap max-h-64 overflow-y-auto">
            {original}
          </div>
        </div>

        {/* Modified */}
        <div className="p-4">
          <div className="text-xs font-medium text-green-600 dark:text-green-400 mb-2">
            修改后
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-300 whitespace-pre-wrap max-h-64 overflow-y-auto">
            {modified}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="bg-gray-50 dark:bg-gray-700 px-4 py-3 border-t dark:border-gray-600 flex items-center justify-between">
        <div className="text-xs text-gray-500 dark:text-gray-400">
          {isDifferent
            ? `检测到 ${original.length} → ${modified.length} 字符`
            : '内容无变化'}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onReject}
            className="px-3 py-1.5 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
          >
            拒绝
          </button>
          <button
            onClick={onAccept}
            className="px-3 py-1.5 text-sm bg-green-600 hover:bg-green-700 text-white rounded-md"
          >
            接受
          </button>
        </div>
      </div>
    </div>
  );
}
