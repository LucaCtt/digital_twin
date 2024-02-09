import { Table, List } from "flowbite-react";

const SimulatedRoutineDetails = ({ routine }) => {
  const when = new Date();
  when.setHours(...routine.when[1].split(":"));

  const details = {
    "Routine name:": routine.name,
    "Activates at:": when.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
    "Actions:": (
      <List className="list-outside dark:text-white">
        {routine.actions.map((action) => (
          <List.Item key={routine.id + " " + action.id}>
            Set the <i>{action.appliance.device}</i>{" "}
            {action.appliance.location && (
              <span>located in the {action.appliance.location}</span>
            )}{" "}
            to <i>{action.mode.name}</i> for{" "}
            {action.duration ? (
              <span>{action.duration} minutes</span>
            ) : (
              <span>until the end of the day</span>
            )}
          </List.Item>
        ))}
      </List>
    ),
  };

  return (
    <Table className="m-0 rounded-lg text-left text-sm dark:text-white rtl:text-right">
      <Table.Body>
        {Object.entries(details).map(([name, value]) => (
          <Table.Row
            key={name}
            className="bg-gray-50 dark:border-gray-800 dark:bg-gray-700"
          >
            <Table.Cell className="whitespace-nowrap font-bold text-gray-900 dark:text-white">
              {name}
            </Table.Cell>
            <Table.Cell>{value}</Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table>
  );
};

export default SimulatedRoutineDetails;
