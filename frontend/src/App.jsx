import { useState } from 'react';
import InputForm from './components/InputForm';
import CalendarView from './components/CalendarView';

function App() {
  const [calendar, setCalendar] = useState(null);
  const [inputData, setInputData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCalendarGenerated = (newCalendar, formData) => {
    setCalendar(newCalendar);
    setInputData(formData);
    setError(null);
  };

  const handleError = (err) => {
    setError(err);
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🎯 Reddit Mastermind
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                AI-powered Reddit content calendar generator
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-400">Powered by OpenAI GPT-4</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <p className="font-medium">Error</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <div className="lg:sticky lg:top-8 h-fit">
            <InputForm
              onCalendarGenerated={handleCalendarGenerated}
              onError={handleError}
              loading={loading}
              setLoading={setLoading}
            />
          </div>

          {/* Calendar View */}
          <div>
            {calendar ? (
              <CalendarView
                calendar={calendar}
                inputData={inputData}
                onNextWeek={handleCalendarGenerated}
                onError={handleError}
                loading={loading}
                setLoading={setLoading}
              />
            ) : (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
                <div className="text-6xl mb-4">📅</div>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  No Calendar Yet
                </h3>
                <p className="text-gray-500">
                  Fill in the form on the left to generate your first Reddit content calendar
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            Built for high-quality, authentic Reddit engagement • Not spam, but strategy
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
