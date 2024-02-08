import { List } from "flowbite-react";

const MostConsumingAppliances = ({ appliancesConsumption, className }) => (
  <div
    className={`flex lg:max-w-sm flex-col justify-between rounded-lg bg-gray-100 p-8 dark:bg-gray-800 ${className}`}
  >
    <h2>Most Consuming Appliances</h2>
    <div className="flex items-center justify-center h-full">
    <List ordered className="list-outside">
      {appliancesConsumption.map(({ appliance, consumption }) => (
        <List.Item key={appliance.id} className="text-lg">
          <span className="font-bold capitalize">{appliance.device}</span>: {consumption} W
        </List.Item>
      ))}
    </List>
    </div>
  </div>
);

export default MostConsumingAppliances;
