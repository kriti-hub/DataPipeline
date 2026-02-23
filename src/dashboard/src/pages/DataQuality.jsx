import PageContainer from "../components/layout/PageContainer";
import PipelineRunsTable from "../components/quality/PipelineRunsTable";
import DQScorecard from "../components/quality/DQScorecard";
import FreshnessIndicator from "../components/quality/FreshnessIndicator";
import { useMultiDataLoader } from "../hooks/useDataLoader";

const DATA_FILES = ["dq_scores.json", "pipeline_runs.json"];

export default function DataQuality() {
  const { data, loading, error } = useMultiDataLoader(DATA_FILES);
  const dqScores = data["dq_scores.json"];
  const pipelineRuns = data["pipeline_runs.json"];

  if (loading) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center py-32">
          <div className="w-8 h-8 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-gray-500">Loading quality metrics...</p>
        </div>
      </PageContainer>
    );
  }

  if (error) {
    return (
      <PageContainer>
        <div className="text-center py-32">
          <p className="text-red-600 font-medium">Failed to load data</p>
          <p className="text-gray-500 text-sm mt-1">{error}</p>
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div className="mb-8">
        <h1 className="section-heading">Data Quality Monitor</h1>
        <p className="section-subheading">Pipeline health, data quality scores, and validation results</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-1">
          <FreshnessIndicator pipelineRuns={pipelineRuns} />
        </div>
        <div className="lg:col-span-2">
          <DQScorecard scores={dqScores} />
        </div>
      </div>

      <PipelineRunsTable runs={pipelineRuns} />
    </PageContainer>
  );
}
