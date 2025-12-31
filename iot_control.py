import paho.mqtt.client as mqtt

class IOTConnection():

    def __init__(self, topic="home/central", broker="broker.hivemq.com"):
        self.topic = topic                                    # declare variables
        self.broker = broker
        self.client = mqtt.Client()

        self.client.connect(self.broker, 1883, 60)             # init client


    def _send_to_topic(self, message):
        """
        Function that sends information to the topic.
        """
        self.client.publish(self.topic, message)
        
        

        
