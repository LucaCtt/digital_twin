import { Table } from "flowbite-react";
import {
  MdKitchen,
  MdLocalFireDepartment,
  MdMicrowave,
  MdLightbulb,
  MdRadio,
  MdTv,
  MdComputer,
  MdAcUnit,
  MdLocalLaundryService,
  MdWaterDrop,
} from "react-icons/md";

const iconMap = {
  fridge: MdKitchen,
  boiler: MdLocalFireDepartment,
  microwave: MdMicrowave,
  lamp: MdLightbulb,
  radio: MdRadio,
  television: MdTv,
  computer: MdComputer,
  "air cond": MdAcUnit,
  "washing machine": MdLocalLaundryService,
  "dish washer": MdWaterDrop,
};

const getIcon = (device) => {
  for (const [key, Icon] of Object.entries(iconMap)) {
    if (
      device.toLowerCase().includes(key) ||
      key.includes(device.toLowerCase())
    ) {
      return <Icon className="h-4 w-4 self-center" />;
    }
  }
};

const AppliancesList = ({ appliances }) => {
  return (
    <div className="flex flex-col justify-start rounded-lg bg-gray-100 p-8 dark:bg-gray-800">
      <h2>Appliances</h2>
      <div className="max-h-screen overflow-auto">
        <Table striped hoverable>
          <Table.Head>
            <Table.HeadCell>Device</Table.HeadCell>
            <Table.HeadCell>Manufacturer</Table.HeadCell>
            <Table.HeadCell>Model</Table.HeadCell>
            <Table.HeadCell>Location</Table.HeadCell>
            <Table.HeadCell>Operation Modes</Table.HeadCell>
          </Table.Head>
          <Table.Body>
            {appliances.map((appliance) => (
              <Table.Row key={appliance.id}>
                <Table.Cell className="inline-flex items-baseline gap-2 capitalize">
                  {getIcon(appliance.device)}
                  {appliance.device}
                </Table.Cell>
                <Table.Cell className="capitalize">
                  {appliance.manufacturer}
                </Table.Cell>
                <Table.Cell>{appliance.model}</Table.Cell>
                <Table.Cell className="capitalize">
                  {appliance.location}
                </Table.Cell>
                <Table.Cell className="capitalize">
                  {appliance.modes.map((m) => m.name).join(", ")}
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </div>
    </div>
  );
};

export default AppliancesList;
