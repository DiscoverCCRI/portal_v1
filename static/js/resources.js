const STAT_CAP = {
    't12': 'TEROS-12',
    't21': 'TEROS-21',
    'tts': 'Thermistor Temperature Sensor',
    'tsl259': 'TSL25911FN',
    'bme': 'BME280',
    'icm': 'ICM20948',
    'ltr': 'LTR390-UV-1',
    'sgp': 'SGP40', 
    'jetson': 'Jetson Nano',
    'cws': 'Compact Weather Sensor'
}

const ROVER_CAP = {
    'rasPi': 'Raspberry Pi',
    'camera': 'Camera',
    'modem': 'Modem',
    'lidar': 'LIDAR',
    'gps': 'GPS'
}

const DRONE_CAP = {
    'gimbal': 'Gimbal and RGB/IR Camera',
    'lidar': 'LIDAR',
    'jetson': 'Jetson Nano',
    'sdr': 'Software Defined Radio',
    '5g': '5G module(s)'
}
/*
    Delete elements child nodes
*/
function deleteExistingChildNodes( instance )
{
    while( instance.firstChild )
    {
        instance.removeChild( instance.firstChild );
    }
}

/*
    Get caps based on resource type
*/
function capabilityFields( choice )
{
    let cap = {};
    switch( choice )
    {
            case "Stationary":
                cap = STAT_CAP;
                break;
            case "Rover":
                cap = ROVER_CAP;
                break;
            case "Drone":
                cap = DRONE_CAP;
                break;
    }

    return cap;
}

/*
    Generate capabilities based on resource types
*/
function generateFields( capabilities, choice )
{
    //Get caps for resource type
    let cap = capabilityFields( choice );

    //Delete already existing cap fields
    deleteExistingChildNodes( capabilities );

    let newDiv = document.createElement("div");
    
    let index = 0

    //Take each memeber of the cap map and use its key value pair
    Object.entries( cap ).forEach( ( [ key, value ] ) => 
    {
        let id = "id_capabilities_" + index;

        //Create a new label to hold input and set attr
        let newLabel = document.createElement("label");
        newLabel.htmlFor = id;
        newLabel.textContent = value;

        //Create and set checkbox attr
        let newInput = document.createElement("input");
        newInput.id = id;
        newInput.type = "checkbox";
        newInput.name = "capabilities";
        newInput.value = key;
        newInput.style = "margin-right: 10px; margin-left: 3px;";

        newLabel.appendChild( newInput );

        //Create new row each three elements
        if( index != 0 && index % 3 == 0 )
        {
            let newBreak = document.createElement("br");

            newDiv.appendChild( newBreak );
        }

        newDiv.appendChild( newLabel );

        index++;
    })

    capabilities.appendChild( newDiv );
}

/*
    On page load, produce a cap list for selected resource type
*/
document.addEventListener('DOMContentLoaded', function() {
    let capabilities = document.getElementById("id_capabilities");

    //delete preset django choice nodes
    deleteExistingChildNodes( capabilities );

    let resourceType = document.getElementById("id_resourceType");

    //Generate new set of caps based on selected resource type
    resourceType.addEventListener("change", function(){
        generateFields( capabilities, resourceType.value );
    });
});