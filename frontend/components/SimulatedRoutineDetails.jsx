import { Table, List } from "flowbite-react";

const SimulatedRoutineDetails = ({ routine }) => {
  const details = routine && {
    "Routine name:": routine.name,
    "Activates at:": routine.when,
    Actions: (
      <List>
        {routine.actions.map((action) => {
          <List.Item>{`Set ${action.device} to ${action.state} for ${action.duration} minutes`}</List.Item>;
        })}
      </List>
    ),
  };

  return (
    <Table className="m-0 rounded-lg bg-white text-left text-sm dark:bg-gray-900 dark:text-white rtl:text-right">
      <Table.Body className="divide-y">
        {details.map((name, value) => (
          <Table.Row
            key={name}
            className="bg-white dark:border-gray-700 dark:bg-gray-800"
          >
            <Table.Cell className="text-bold whitespace-nowrap font-medium text-gray-900 dark:text-white">
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
