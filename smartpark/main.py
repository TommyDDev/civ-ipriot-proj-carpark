from parking_lot import ParkingLot


def get_message(client, userdata, message):
    message = message.payload.decode('UTF-8')
    print(message)
    # if car entering
    #    process the car
    # if car exiting
    #    process the car
    # if xyz
    #    do something

parking_lot = ParkingLot()
parking_lot.create_mqtt_client()



if __name__=='__main__':
    parking_lot.mqtt_client.client.subscribe("carpark/Moondalup/parking-lot/controller")
    parking_lot.mqtt_client.client.on_message = get_message
    print(parking_lot.mqtt_client.name)
    print(parking_lot.mqtt_client.topic)
    print(parking_lot.location)
    print(parking_lot.total_spaces)



    parking_lot.mqtt_client.client.loop_forever()