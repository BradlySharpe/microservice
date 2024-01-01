import { Connection, ConsumeMessage } from "amqplib";
import { IQueueMessage } from "../interfaces/IQueueMessage";
import { DynamiteController } from "../controllers/DynamiteController";

const QUEUE_NAME = process.env.QUEUE_JOBS;

export class Jobs {
    public static async createQueueListener(connection: Connection) {
        const channel = await connection.createChannel();
        await channel.assertQueue(QUEUE_NAME, { durable: false });

        channel.consume(QUEUE_NAME, Jobs.consumeMessage);
    }

    public static async consumeMessage(message: ConsumeMessage) {
        const receivedMessage: IQueueMessage = JSON.parse(message.content.toString());

        if (receivedMessage == null)
            return;

            switch (`${receivedMessage.key}`.toUpperCase()) {
                case "CHECK_CACHE":
                    await DynamiteController.getJobs();
                    break;
    
                case "UPDATE":
                    await DynamiteController.fetchDynamiteJobs();
                    break;
            
                default:
                    console.log(`Received unknown message`, receivedMessage);
                    break;
            }
    }
}