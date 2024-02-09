import { useContext } from "react";
import { List, Table } from "flowbite-react";
import { DigitalTwinContext } from "./DigitalTwinContextProvider";

const RoutinesSection = () => {
  const { routines } = useContext(DigitalTwinContext);

  return (
    <div className="flex flex-col justify-start rounded-lg bg-gray-100 p-8 dark:bg-gray-800">
      <h2>Routines</h2>
      <div className="max-h-screen overflow-auto">
        <Table striped hoverable>
          <Table.Head>
            <Table.HeadCell>Name</Table.HeadCell>
            <Table.HeadCell>Activates at</Table.HeadCell>
            <Table.HeadCell>Enabled</Table.HeadCell>
            <Table.HeadCell>Actions</Table.HeadCell>
          </Table.Head>
          <Table.Body>
            {routines.map((routine) => (
              <Table.Row key={routine.id}>
                <Table.Cell>{routine.name}</Table.Cell>
                <Table.Cell>
                  {new Date(routine.when).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </Table.Cell>
                <Table.Cell>{routine.enabled ? "Yes" : "No"}</Table.Cell>
                <Table.Cell>
                  <List>
                    {routine.actions.map((action) => {
                      return (
                        <List.Item key={routine.id + " " + action.id}>
                          Set the <i>{action.appliance.device}</i>{" "}
                          {action.appliance.location && (
                            <span>
                              located in the {action.appliance.location}
                            </span>
                          )}{" "}
                          to <i>{action.mode.name}</i> for{" "}
                          {action.duration ? (
                            <span>{action.duration} minutes</span>
                          ) : (
                            <span>until the end of the day</span>
                          )}
                          .
                        </List.Item>
                      );
                    })}
                  </List>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </div>
    </div>
  );
};

export default RoutinesSection;
