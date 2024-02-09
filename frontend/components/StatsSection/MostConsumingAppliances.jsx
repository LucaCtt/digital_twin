import { List } from "flowbite-react";

const MostConsumingAppliances = ({ appliancesConsumption, className }) => (
  <div
    className={`flex flex-col justify-between rounded-lg bg-gray-100 p-8 dark:bg-gray-800 lg:max-w-sm ${className}`}
  >
    <h2>Most Consuming Appliances</h2>
    <div className="flex h-full items-center justify-center">
      <List ordered className="list-outside">
        {appliancesConsumption.map(({ appliance, consumption }) => (
          <List.Item key={appliance.id} className="text-lg">
            <span className="font-bold capitalize">{appliance.device}</span>:{" "}
            {consumption} W
          </List.Item>
        ))}
      </List>
    </div>
  </div>
);

export default MostConsumingAppliances;
