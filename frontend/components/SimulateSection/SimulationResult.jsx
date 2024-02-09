import { List } from "flowbite-react";

const ErrorsList = ({ errors }) => {
  return (
    <div>
      <h3 className="text-lg font-semibold">Errors</h3>
      <List>
        {errors.map((error, index) => (
          <List.Item key={index}>{error.message}</List.Item>
        ))}
      </List>
    </div>
  );
};

const RecommendationsList = ({ recommendations }) => {
  return (
    <div>
      <h3 className="text-lg font-semibold">Recommendations</h3>
      <ul>
        {recommendations.map((recommendation, index) => (
          <li key={index}>{recommendation.message}</li>
        ))}
      </ul>
    </div>
  );
};

const SimulationResult = ({ errors, recommendations, className }) => {
  const hasErrors = errors && errors.length > 0;
  const hasRecommendations = recommendations && recommendations.length > 0;
  const hasResults = hasErrors || hasRecommendations;

  return (
    <div
      className={`flex rounded-lg bg-gray-50 p-4 dark:bg-gray-700 ${!hasResults && "items-center justify-center"} ${className}`}
    >
      {hasResults ? (
        <div className="flex flex-col gap-8">
          {hasErrors && <ErrorsList errors={errors} />}
          {hasRecommendations && (
            <RecommendationsList recommendations={recommendations} />
          )}
        </div>
      ) : (
        <p>Simulation results will be shown here</p>
      )}
    </div>
  );
};

export default SimulationResult;
