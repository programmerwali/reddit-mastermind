import { useState } from 'react';
import { api } from '../utils/api';
import LoadingSpinner from './LoadingSpinner';


// Sample data for quick testing
const SAMPLE_DATA = {
  company_info: "SlideForge - AI-powered presentation tool that automates slide design, formatting, and layout for professionals who want beautiful decks without the design hassle",
  personas: [
    {
      username: "riley_ops",
      info: "Operations head at a SaaS startup, detail-oriented perfectionist who struggles with presentation design but values precision and clean formatting"
    },
    {
      username: "jordan_consults",
      info: "Independent consultant working with early stage founders, values storytelling and believes strong slides can change the energy of a room"
    },
    {
      username: "emily_econ",
      info: "Economics student who became the unofficial slide maker for every group project, perfectionist who can't stand seeing good research trapped in ugly slides"
    }
  ],
  subreddits: ["r/PowerPoint", "r/startups", "r/productivity", "r/consulting"],
  keywords: ["best ai presentation maker", "pitch deck generator", "automate presentations", "alternatives to PowerPoint"],
  posts_per_week: 3
};

function InputForm({ onCalendarGenerated, onError, loading, setLoading }) {
  const [companyInfo, setCompanyInfo] = useState('');
  const [personas, setPersonas] = useState([{ username: '', info: '' }]);
  const [subreddits, setSubreddits] = useState('');
  const [keywords, setKeywords] = useState('');
  const [postsPerWeek, setPostsPerWeek] = useState(3);

  const loadSampleData = () => {
    setCompanyInfo(SAMPLE_DATA.company_info);
    setPersonas(SAMPLE_DATA.personas);
    setSubreddits(SAMPLE_DATA.subreddits.join(', '));
    setKeywords(SAMPLE_DATA.keywords.join(', '));
    setPostsPerWeek(SAMPLE_DATA.posts_per_week);
  };

  const addPersona = () => {
    setPersonas([...personas, { username: '', info: '' }]);
  };

  const removePersona = (index) => {
    if (personas.length > 1) {
      setPersonas(personas.filter((_, i) => i !== index));
    }
  };

  const updatePersona = (index, field, value) => {
    const updated = [...personas];
    updated[index][field] = value;
    setPersonas(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    onError(null);

    try {
      // Validate inputs
      if (!companyInfo.trim()) {
        throw new Error('Company info is required');
      }
      
      if (personas.length < 2) {
        throw new Error('At least 2 personas are required');
      }

      for (let persona of personas) {
        if (!persona.username.trim() || !persona.info.trim()) {
          throw new Error('All personas must have username and info');
        }
      }

      // Parse subreddits and keywords
      const subredditList = subreddits.split(',').map(s => s.trim()).filter(s => s);
      const keywordList = keywords.split(',').map(k => k.trim()).filter(k => k);

      if (subredditList.length === 0) {
        throw new Error('At least one subreddit is required');
      }

      if (keywordList.length === 0) {
        throw new Error('At least one keyword is required');
      }

      // Call API
      const calendar = await api.generateCalendar({
        company_info: companyInfo,
        personas: personas,
        subreddits: subredditList,
        keywords: keywordList,
        posts_per_week: postsPerWeek
      });

      onCalendarGenerated(calendar, {
        company_info: companyInfo,
        personas: personas,
        subreddits: subredditList,
        keywords: keywordList,
        posts_per_week: postsPerWeek
      });
    } catch (err) {
      onError(err.response?.data?.error || err.message || 'Failed to generate calendar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Input Configuration</h2>
        <button
          type="button"
          onClick={loadSampleData}
          className="text-sm text-orange-600 hover:text-orange-700 font-medium"
        >
          Load Sample Data
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Company Info */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Company Info *
          </label>
          <textarea
            value={companyInfo}
            onChange={(e) => setCompanyInfo(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            rows="3"
            placeholder="e.g., SlideForge - AI presentation tool that..."
            required
          />
        </div>

        {/* Personas */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Personas * (min. 2)
            </label>
            <button
              type="button"
              onClick={addPersona}
              className="text-sm text-orange-600 hover:text-orange-700 font-medium"
            >
              + Add Persona
            </button>
          </div>
          <div className="space-y-4">
            {personas.map((persona, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">
                    Persona {index + 1}
                  </span>
                  {personas.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removePersona(index)}
                      className="text-sm text-red-600 hover:text-red-700"
                    >
                      Remove
                    </button>
                  )}
                </div>
                <input
                  type="text"
                  value={persona.username}
                  onChange={(e) => updatePersona(index, 'username', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-2 focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  placeholder="Username (e.g., riley_ops)"
                  required
                />
                <textarea
                  value={persona.info}
                  onChange={(e) => updatePersona(index, 'info', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  rows="3"
                  placeholder="Persona background and personality..."
                  required
                />
              </div>
            ))}
          </div>
        </div>

        {/* Subreddits */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Subreddits * (comma-separated)
          </label>
          <input
            type="text"
            value={subreddits}
            onChange={(e) => setSubreddits(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            placeholder="r/PowerPoint, r/startups, r/productivity"
            required
          />
        </div>

        {/* Keywords */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Keywords * (comma-separated)
          </label>
          <input
            type="text"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            placeholder="best ai presentation maker, pitch deck generator"
            required
          />
        </div>

        {/* Posts Per Week */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Posts Per Week
          </label>
          <input
            type="number"
            value={postsPerWeek}
            onChange={(e) => setPostsPerWeek(parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            min="1"
            max="10"
            required
          />
        </div>
        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center"
        >
          {loading ? (
            <>
              <LoadingSpinner />
              <span>Generating Calendar... (30-60s)</span>
            </>
          ) : (
            '🚀 Generate Calendar'
          )}
        </button>
      </form>
    </div>
  );
}

export default InputForm;
