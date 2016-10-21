
  google.charts.load("current", {packages:["sankey"]});
  google.charts.setOnLoadCallback(drawChart);

function uniq(a) {
    var seen = {};
    return a.filter(function(item) {
        return seen.hasOwnProperty(item) ? false : (seen[item] = true);
    });
}

  function drawChart() {
    $.get("SFHomeless_individ_features_strings_parsed.csv", function(csvString) {
            // transform the CSV string into a 2-dimensional array
      var arrayData = $.csv.toArrays(csvString, {onParseValue: $.csv.hooks.castToScalar});
      // console.log(arrayData);
       var data = new google.visualization.DataTable();
    
      var allRaces = [];
      var allEthnicity = [];
      var allGenders = [];
      var allVeteran = [];
      var allChronic = [];
      var allViolence = [];
      var allAge = [];

for (var i = 1; i < arrayData.length; i++) { //loop of all data in the array

  allRaces.push(arrayData[i][10]);
  allEthnicity.push(arrayData[i][7]); 
  allGenders.push(arrayData[i][1]);
  allVeteran.push(arrayData[i][11]);
  allChronic.push(arrayData[i][3]);
  allViolence.push(arrayData[i][9]);
  allAge.push(arrayData[i][6]);

}

allRaces = uniq(allRaces);
allEthnicity = uniq(allEthnicity);
allGenders = uniq(allGenders);
allVeteran = uniq(allVeteran);
allChronic = uniq(allChronic);
allViolence = uniq(allViolence);
allAge = uniq(allAge);


console.log(allRaces);
console.log(allEthnicity);
console.log(allGenders);
console.log(allVeteran);
console.log(allChronic);
console.log(allViolence);
console.log(allAge);


var FinalDataArray = []; // only need one big array to store everything

// -----------1. Race to Ethnicity-----------//

for (var raceindex = 0; raceindex < allRaces.length; raceindex++) {  
        for (var ethnicityindex = 0; ethnicityindex < allEthnicity.length; ethnicityindex++) { 
                var nowCount = 0; 
                var nowRace = allRaces[raceindex]; 
                var nowEthnicity = allEthnicity[ethnicityindex]; 
                for (var dataIndex = 0; dataIndex < arrayData.length; dataIndex++) { 
                        if(arrayData[dataIndex][10] == nowRace   &&   arrayData[dataIndex][7] == nowEthnicity){
                                nowCount++; 
                              }
                            }
                var miniArray_local = []; 
                miniArray_local.push(nowRace); 
                miniArray_local.push(nowEthnicity); 
                miniArray_local.push(nowCount);
                // console.log(miniArray_local);
                FinalDataArray.push(miniArray_local);
              }
            }

// //-----------2. Ethnicity to Gender-----------//

for (var ethnicityindex = 0; ethnicityindex < allEthnicity.length; ethnicityindex++) { 
        for (var genderindex = 0; genderindex < allGenders.length; genderindex++) {
                var nowCount = 0;  
                var nowEthnicity = allEthnicity[ethnicityindex]; 
                var nowGender = allGenders[genderindex];
                for (var dataIndex = 0; dataIndex < arrayData.length; dataIndex++) { 
                        if(arrayData[dataIndex][7] == nowEthnicity  &&  arrayData[dataIndex][1] == nowGender ){
                                nowCount++; 
                              }
                            }
                var miniArray_local = [];
                miniArray_local.push(nowEthnicity);
                miniArray_local.push(nowGender);
                miniArray_local.push(nowCount);
                // console.log(miniArray_local);
                FinalDataArray.push(miniArray_local);
              }
            }

//-----------3. Gender to Veteran-----------//

for (var genderindex = 0; genderindex < allGenders.length; genderindex++) {  // choose an armed to look for
        for (var veteranindex = 0; veteranindex < allVeteran.length; veteranindex++) {  // choose a classification to look for
                var nowCount = 0;  // start counting with no values
                var nowGender = allGenders[genderindex];// our chosen gender for this loop
                var nowVeteran = allVeteran[veteranindex]; // our chosen veteran for this loop
                for (var dataIndex = 0; dataIndex < arrayData.length; dataIndex++) { //loop of all data in the array looking for the above race and gender
                        if(arrayData[dataIndex][1] == nowGender  &&  arrayData[dataIndex][11] == nowVeteran ){ // if this data object matches our chosen gender and race
                                nowCount++;  //add one value to our item count
                              }
                            }
                var miniArray_local = []; 
                miniArray_local.push(nowGender);
                miniArray_local.push(nowVeteran); 
                miniArray_local.push(nowCount);
                // console.log(miniArray_local);
                FinalDataArray.push(miniArray_local);
              }
            }

//-----------4. Veteran to Chronic-----------//
for (var veteranindex = 0; veteranindex < allVeteran.length; veteranindex++) {
        for (var chronicindex = 0; chronicindex < allChronic.length; chronicindex++) {
                var nowCount = 0;  
                var nowVeteran = allVeteran[veteranindex]; 
                var nowchronic = allChronic[chronicindex];
                for (var dataIndex = 0; dataIndex < arrayData.length; dataIndex++) {
                        if(arrayData[dataIndex][11] == nowVeteran  &&  arrayData[dataIndex][3] == nowchronic ){
                                nowCount++; 
                              }
                            }
                var miniArray_local = []; 
                 miniArray_local.push(nowVeteran); 
                 miniArray_local.push(nowchronic);
                miniArray_local.push(nowCount);
                // console.log(miniArray_local);
                FinalDataArray.push(miniArray_local);
              }
            }

//-----------5. Chronic to Violence-----------//
for (var chronicindex = 0; chronicindex < allChronic.length; chronicindex++) { 
        for (var violenceindex = 0; violenceindex < allViolence.length; violenceindex++) { 
                var nowCount = 0;  
                var nowchronic = allChronic[chronicindex];
                var nowViolence = allViolence[violenceindex]; 
                for (var dataIndex = 0; dataIndex < arrayData.length; dataIndex++) { 
                 
                        if(arrayData[dataIndex][3] == nowchronic   &&  arrayData[dataIndex][9] == nowViolence ){
                                nowCount++;  
                              }
                            }
                var miniArray_local = []; 
                // console.log('in all the data we found this:');
               miniArray_local.push(nowchronic);
                miniArray_local.push(nowViolence);
                miniArray_local.push(nowCount);
                // console.log(miniArray_local);
                FinalDataArray.push(miniArray_local);
              }
            }


//-----------6. Violence to Age-----------//
for (var violenceindex = 0; violenceindex < allViolence.length; violenceindex++) { 
        for (var ageindex = -1; ageindex <= 102; ageindex+=5) {  
                var nowCount = 0;  
                var nowViolence = allViolence[violenceindex];
                var nowAge = ageindex; 
                for (var dataIndex = 0; dataIndex < arrayData.length; dataIndex++) { 

                var inDataAge = arrayData[dataIndex][6];
                       
                        if(arrayData[dataIndex][9] == nowViolence &&  inDataAge > nowAge  && inDataAge <= nowAge+5 ){ 
                                nowCount++;  
                              }
                            }
                var miniArray_local = []; 
                miniArray_local.push(nowViolence);
                miniArray_local.push((nowAge+1) +'-'+(nowAge+5));
                miniArray_local.push(nowCount);
                FinalDataArray.push(miniArray_local);
              }
            }

            // console.log('IN THE END we found this:');
            // console.log(FinalDataArray);

            data.addColumn('string', 'From');
            data.addColumn('string', 'To');
            data.addColumn('number', 'Ammt');
            data.addRows(FinalDataArray); 


//-----------for style----------//

var colors = ['#a6cee3', '#b2df8a', '#fb9a99', '#fdbf6f','#cab2d6', '#ffff99', '#1f78b4', '#33a02c'];

var options = {
  sankey: {
    // iterations: 0, //If set iterations to 0, and the diagram should draw according to the input order of the data.
    
    node: {
      colors: colors,
      labelPadding: 15,
      label: {  color: '#dddddd',
                fontSize: 12, }

    },
    link: {
      colorMode: 'gradient',
      colors: colors
    }
  }
};

        // Instantiate and draw our chart, passing in some options.
        var chart = new google.visualization.Sankey(document.getElementById('sankey_multiple'));
        chart.draw(data, options);


      });
}