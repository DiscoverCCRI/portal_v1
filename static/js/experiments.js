/*
    To be changed: Get rid of global states
*/
var resources = [];
var allResources = [];

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
};

const ROVER_CAP = {
    'rasPi': 'Raspberry Pi',
    'camera': 'Camera',
    'modem': 'Modem',
    'lidar': 'LIDAR',
    'gps': 'GPS'
};

const DRONE_CAP = {
    'gimbal': 'Gimbal and RGB/IR Camera',
    'lidar': 'LIDAR',
    'jetson': 'Jetson Nano',
    'sdr': 'Software Defined Radio',
    '5g': '5G module(s)'
};

/*
    Adds resource to array thats sent to django backend
*/
function addResource( obj )
{
    let uuid = obj.value;

    if( obj.checked && !checkForInArray( uuid ) )
    {
        resources.push( uuid );
    }
    else
    {
        for( let index = 0; index < resources.length; index++ )
        {
            if( uuid == resources[ index ] )
            {
                resources.splice( index, index + 1 );
            }
        }
    }

    addResourceToForm();
}


/*
    Gets all selected caps 
*/
function getAllSelectedCapabilities()
{
    let selectedCapFilter = [];

    let allCapabilities = document.getElementById("cap-holder");

    let children = allCapabilities.children;

    for( let index = 0; index < children.length; index++ )
    {
        if( children[ index ].tagName.toLowerCase() == "label" )
        {
            let inputElement = children[ index ].children;

            if( inputElement[ 0 ].checked )
            {
                selectedCapFilter.push( inputElement[ 0 ].value );
            }
        } 
    }

    return selectedCapFilter;
}

/*
    Parses the strings of form resource name(resource type)
*/
function parseResourceType( string )
{
    let splitResult = string.split('(');

    return { 'name': splitResult[ 0 ], 
             'type': splitResult[ 1 ].split(')')[ 0 ] };
}

/*
    Gets django sent resources and converts them to js object
*/
function getResources()
{
    let resourceDiv = document.getElementById("resources");

    let children = resourceDiv.children;

    //Loop through all resources
    for( let index = 0; index < children.length; index++ )
    {
        //If the id is empty we know it's not a resource object
        if( children[ index ].id != "" )
        {
            //Each input has <a> child that contains name and type
            let nameData = parseResourceType(
                                children[ index + 1 ].innerText );

            let newResource = {
                'name': nameData['name'],
                'type': nameData['type'],
                'href': children[ index + 1 ].href,
                "uuid": children[ index ].value,
                "id": children[ index ].id,
                "capabilities": children[ index + 2 ].innerText
            }

            allResources.push( newResource );
        }
    }
}

/*
    Refresh the resource on type and cap change.
*/
function refreshResourcesFromFilter( type, filter )
{
    let resources = document.getElementById("resources");

    //delete the existing resource nodes
    deleteExistingChildNodes( resources );

    let filteredResources = filterResources( type, filter );

    //Check that there are any resources
    if( filteredResources.length > 0 )
    {
        //Loop through requested resource, making a new element for each
        for( let index = 0; index < filteredResources.length; index++ )
        {
            //Create resource element
            let input = document.createElement("input");
            input.type = 'checkbox';
            input.id = filteredResources[ index ]['id'];
            input.value = filteredResources[ index ]['uuid'];
            input.style = "margin-left: 10px;";
            input.onclick = function() {
                addResource( input );
            };

            //Create link to resouce description
            let link = document.createElement("a");
            link.href = filteredResources[ index ]['href'];
            link.target = "_blank";
            link.textContent = `${ filteredResources[ index ]['name'] }
                                     (${ filteredResources[ index ]['type'] })`;

            //Create container to contain resource caps
            let capContainer = document.createElement("p");
            capContainer.style = "display: none;";
            capContainer.innerText = filteredResources[ index ]['capabilities'];

            //Append the correnspoding children to resource container
            resources.appendChild( input );
            resources.appendChild( link );
            resources.appendChild( capContainer );

            //Every three resources we will incite a new row
            if( ( index + 1 ) % 3 == 0 )
            {
                let lineBreak = document.createElement("br");
                resources.appendChild( lineBreak );
            }
        }
    }
    //Create an element stating there were no resouces found with such filter
    else
    {
        let noResources = document.createElement("p");
        noResources.innerText = "No available resources";
        resources.appendChild( noResources );
    }
}

/*
    Filters resources based on cap and resource type
*/
function filterResources( type, capabilities )
{
    let matchedResources = [];

    let typeResources = [];

    //Get all resource with valid type
    for( let index = 0; index < allResources.length; index++ )
    {
        if( allResources[ index ]['type'] == type )
        {
            typeResources.push( allResources[ index ] );
        }
    }

    //If there are selected capabilities, then we want to filter
    if( capabilities.length > 0 )
    {
        //Loop through all resources of specified type
        for( let outIndex = 0; outIndex < typeResources.length; outIndex++ )
        {
            let resourceMatch = true;

            //Loop through specified capabilities
            for( let innerIndex = 0; innerIndex < capabilities.length; 
                                                                  innerIndex++ )
            {
                //Check for capability in cap array
                if( !typeResources[ outIndex ].capabilities.includes( 
                                                  capabilities[ innerIndex ] ) )
                {
                    resourceMatch = false;
                }
            }

            //Append the resource to matched array
            if( resourceMatch )
            {
                matchedResources.push( typeResources[ outIndex ] );
            }
        }

        return matchedResources;
    }

    return typeResources;
}

/*
    Updates the forms value to be sent to django backend
*/
function addResourceToForm()
{
    let resourceForm = document.getElementById("id_resources");

    resourceForm.value = resources;
}

/*
    Checks if a resource is already selected
*/
function checkForInArray( uuid )
{
    let check = false;

    for( let resource in resources )
    {
        if( uuid == resource )
        {
            check = true;
        }
    }

    return check;
}

/*
    Removes all child nodes of a given element 
*/
function deleteExistingChildNodes( instance )
{
    while( instance.firstChild )
    {
        instance.removeChild( instance.firstChild );
    }
}

/*
    Takes in the resource type choice and returns cap map 
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
    Creates new capability fields. 
*/
function generateFields( capabilities, choice )
{
    //Get cap for choosen resource type
    let cap = capabilityFields( choice );

    //Delete prev capabilities to display new
    deleteExistingChildNodes( capabilities );

    //Create a new container to hold new cap
    let newDiv = document.createElement("div");
    newDiv.id = "cap-holder";

    //Get section where to display that there is no cap for resource type
    let noCapabilities = document.getElementById("no_capabilities");
    
    //Index here is used to give element unique id 
    let index = 0;

    //We need to check the cap length to ensure we have cap for resource type
    if( cap.length != 0 )
    {
        //Hide no cap section so we can display caps
        noCapabilities.style.visibility = "hidden";

        //Take each item in map and use its key and pair
        Object.entries( cap ).forEach( ( [ key, value ] ) => 
        {
            let id = "id_capabilities_" + index;

            //Create a label to containerize the new input
            let newLabel = document.createElement("label");
            newLabel.htmlFor = id;
            newLabel.textContent = value;

            //Create a new input for cap
            let newInput = document.createElement("input");

            //Set input attributes
            newInput.id = id;
            newInput.type = "checkbox";
            newInput.name = "capabilities";
            newInput.value = key;
            newInput.style = "margin-right: 10px; margin-left: 3px;";
            
            //Everytime a cap is selected, we want to filter the resource again
            newInput.onclick = function() {
                let resourceType = document.getElementById("id_resourceType");

                let filter = getAllSelectedCapabilities();

                refreshResourcesFromFilter( resourceType.value, filter ); 
            }

            //Add the cap input to label container
            newLabel.appendChild( newInput );

            //Every three cap in a row we will make a new row
            if( index != 0 && index % 3 == 0 )
            {
                let newBreak = document.createElement("br");

                newDiv.appendChild( newBreak );
            }

            newDiv.appendChild( newLabel );

            index++;
        })
    }
    else
    {
        noCapabilities.style.display = "none";
    }

    capabilities.appendChild( newDiv );
}

//Instatiate cap/resource content on page load
document.addEventListener('DOMContentLoaded', function() {
    //Get rid of django preset static UI
    var capabilities = document.getElementById("id_capability_filter");

    //Get all django resources
    getResources();

    //delete preset django choice nodes
    deleteExistingChildNodes( capabilities );

    //Get pre-set django elements
    let resourceType = document.getElementById("id_resourceType");

    //To be used for django hook in, no need to show.
    let resourceForm = document.getElementById("id_resources");

    //Get rid of djano pre-set UI 
    deleteExistingChildNodes( resourceForm );

    //Filter resources on type only upon first load 
    refreshResourcesFromFilter( resourceType.value, [] );

    resourceForm.style.display = "none";

    //Each time a resource type changes we want to show correspording cap fields
    // and refilter resource by selected type
    resourceType.addEventListener("change", function(){
        generateFields( capabilities, resourceType.value );
        refreshResourcesFromFilter( resourceType.value, [] );
    });
});