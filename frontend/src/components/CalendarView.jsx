import { useState } from 'react';
import { api } from '../utils/api';
import LoadingSpinner from './LoadingSpinner';

function CalendarView({ calendar, inputData, onNextWeek, onError, loading, setLoading }) {
  const [expandedPosts, setExpandedPosts] = useState({});

  const togglePost = (postId) => {
    setExpandedPosts(prev => ({
      ...prev,
      [postId]: !prev[postId]
    }));
  };

  const handleGenerateNextWeek = async () => {
    setLoading(true);
    onError(null);

    try {
      const nextCalendar = await api.generateNextWeek({
        ...inputData,
        week_number: calendar.week + 1,
        previous_calendar: calendar
      });

      onNextWeek(nextCalendar, inputData);
    } catch (err) {
      onError(err.response?.data?.error || err.message || 'Failed to generate next week');
    } finally {
      setLoading(false);
    }
  };

  const exportAsJSON = () => {
    const dataStr = JSON.stringify(calendar, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `reddit-calendar-week-${calendar.week}.json`;
    link.click();
  };

  const getScoreColor = (score) => {
    if (score >= 9) return 'text-green-600';
    if (score >= 7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score) => {
    if (score >= 9) return 'bg-green-100';
    if (score >= 7) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">
              Week {calendar.week} Calendar
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              {calendar.start_date} to {calendar.end_date}
            </p>
          </div>
          <div className="text-right">
            <div className={`text-4xl font-bold ${getScoreColor(calendar.quality_score)}`}>
              {calendar.quality_score}/10
            </div>
            <p className="text-xs text-gray-500 mt-1">Quality Score</p>
          </div>
        </div>

        {/* Quality Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-4">
          {Object.entries(calendar.metrics).map(([key, value]) => {
            if (key === 'warnings' || key === 'overall_score') return null;
            return (
              <div key={key} className={`p-3 rounded-lg ${getScoreBgColor(value)}`}>
                <div className={`text-lg font-bold ${getScoreColor(value)}`}>
                  {value}/10
                </div>
                <div className="text-xs text-gray-600 capitalize">
                  {key.replace(/_/g, ' ')}
                </div>
              </div>
            );
          })}
        </div>

        {/* Warnings */}
        {calendar.metrics.warnings && calendar.metrics.warnings.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
            <h4 className="text-sm font-semibold text-yellow-800 mb-2">⚠️ Warnings</h4>
            <ul className="text-sm text-yellow-700 space-y-1">
              {calendar.metrics.warnings.map((warning, index) => (
                <li key={index}>• {warning}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={handleGenerateNextWeek}
            disabled={loading}
            className="flex-1 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-2 px-4 rounded-lg transition-colors text-sm flex items-center justify-center"
          >
            {loading ? (
              <>
                <LoadingSpinner />
                <span>Generating Week {calendar.week + 1}...</span>
              </>
            ) : (
              '➡️ Generate Next Week'
            )}
          </button>
          <button
            onClick={exportAsJSON}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-lg transition-colors text-sm"
          >
            📥 Export JSON
          </button>
        </div>
      </div>

      {/* Posts */}
      <div className="space-y-4">
        {calendar.posts.map((post) => (
          <div key={post.post_id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            {/* Post Header */}
            <div
              className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => togglePost(post.post_id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs font-semibold rounded">
                      {post.subreddit}
                    </span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded">
                      u/{post.author_username}
                    </span>
                    <span className="text-xs text-gray-500">
                      {post.timestamp}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-1">
                    {post.title}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {post.body}
                  </p>
                </div>
                <div className="ml-4 text-gray-400">
                  {expandedPosts[post.post_id] ? '▼' : '▶'}
                </div>
              </div>
            </div>

            {/* Comments (Expanded) */}
            {expandedPosts[post.post_id] && (
              <div className="border-t border-gray-200 bg-gray-50 p-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-3">
                  💬 Comments ({post.comments.length})
                </h4>
                <div className="space-y-3">
                  {post.comments.map((comment) => (
                    <div
                      key={comment.comment_id}
                      className={`p-3 rounded-lg ${
                        comment.parent_comment_id ? 'ml-8 bg-white' : 'bg-white'
                      } border border-gray-200`}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-semibold text-gray-700">
                          u/{comment.username}
                        </span>
                        <span className="text-xs text-gray-500">
                          {comment.delay_minutes} min after {comment.parent_comment_id ? 'previous' : 'post'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-800">{comment.comment_text}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default CalendarView;