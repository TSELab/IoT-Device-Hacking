function assert(condition, message) {
    if (!condition) throw new Error("assert: " + message);
}

function requestJson(uri, callback) {
    var request = new XMLHttpRequest();
    request.open('GET', '/licenses/packages.json', true);
    request.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            var data = JSON.parse(this.responseText);
            callback(null, data);
        } else {
            callback(this.status);
            }
        }

    request.send();
    request = null;
}

function buildTitle(data) {
    assert(data.Package, "missing package name");
    assert(data.Version, "missing version number");

    return "<h2>" + data.Package + ' ' + data.Version + "</h2>";
}

function buildAttributions(data) {
    var result = "";
    if (data.Attributions) {
        for (var i = 0; i < data.Attributions.length; i++) {
            result += data.Attributions[i] + "<br>";
        }
    }

    return result;
}

function buildWebsite(data) {
    if (!data.Website) return "";

    return 'Website: <a href="' + data.Website + '">' + data.Website + "</a><br>"
}

function buildLicense(data) {
    assert(Object.keys(data.licenses).length > 0, "no license present");
    assert(Object.keys(data.licenses).length <= 1, "more than 1 license");

    var result = "License(s): ";
    var licensesNames = Object.keys(data.licenses)
    for (var i = 0; i < licensesNames.length; i++) {
        result += '<a href = "/licenses/' + data.licenses[licensesNames[i]] + '">' + licensesNames[i] + "</a>, "
    }

    /* remove last ", " from the string */
    return result.substr(0, result.length - 2)
}                                                              
                                                               
function buildContainerEntry(data) {                                                                      
    return buildTitle(data) +                                  
            "<p>" +                                            
            buildAttributions(data) +                          
            buildWebsite(data) +                                
            buildLicense(data) +                                
            "</p>"                
    ;                               
}                            
                                                         
function populateContainer(data) {                       
    var content = "";                       
                                                                                 
    for (var i = 0; i < data.length; i++) {     
        content += buildContainerEntry(data[i]);               
    }                                                          
                                                                        
    container = document.getElementById("licenses-placeholder");          
    container.outerHTML = content;
}                               
                                                  
function main() {                                        
    requestJson('/packages.json', function(error, data) {                                                 
        if (!error) populateContainer(data);
    });                                                         
}                                         
                                                               
document.addEventListener("DOMContentLoaded", function(event) {
    main();    
}
