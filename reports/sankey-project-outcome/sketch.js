
  google.charts.load("current", {packages:["sankey"]});
  google.charts.setOnLoadCallback(drawChart);

function uniq(a) {
    var seen = {};
    return a.filter(function(item) {
        return seen.hasOwnProperty(item) ? false : (seen[item] = true);
    });
}

  function drawChart() {
    // $.get("SFHomeless_individ_features_strings_parsed.csv", function(csvString) {
      $.get("homeless_3_projects_outcome_parsed.csv", function(csvString) {
            // transform the CSV string into a 2-dimensional array
      var arrayData = $.csv.toArrays(csvString, {onParseValue: $.csv.hooks.castToScalar});
      console.log(arrayData);
       var data = new google.visualization.DataTable();
    
      var allRaces = [];
      var allEthnicity = [];
      var allGenders = [];
      var allVeteran = [];
      var allAge = [];
      var allStatus = [];
      var allProject1 = [];
      var allProject2 = [];
      var allProject3 = [];
      var allPermanentHousing = [];

for (var i = 1; i < arrayData.length; i++) { //loop of all data in the array

  allRaces.push(arrayData[i][1]);
  allEthnicity.push(arrayData[i][2]); 
  allGenders.push(arrayData[i][3]);
  allVeteran.push(arrayData[i][4]);
  allAge.push(arrayData[i][6]);
  allStatus.push(arrayData[i][8]);
  allProject1.push(arrayData[i][9]);
  allProject2.push(arrayData[i][10]);
  allProject3.push(arrayData[i][11]);
  allPermanentHousing.push(arrayData[i][12]);
}

allRaces = uniq(allRaces);
allEthnicity = uniq(allEthnicity);
allGenders = uniq(allGenders);
allVeteran = uniq(allVeteran);
allAge = uniq(allAge);
allStatus = uniq(allStatus);
allProject1 = uniq(allProject1);
allProject2 = uniq(allProject2);
allProject3 = uniq(allProject3);
allPermanentHousing = uniq(allPermanentHousing);

console.log(allRaces);
console.log(allEthnicity);
console.log(allGenders);
console.log(allVeteran);
console.log(allAge);
console.log(allStatus);
console.log(allProject1);
console.log(allProject2);
console.log(allProject3);
console.log(allPermanentHousing);


var FinalDataArray = []; // only need one big array to store everything

// -----------1. Race to Ethnicity-----------//

for (var raceindex = 0; raceindex < allRaces.length; raceindex++) {  
        for (var ethnicityindex = 0; ethnicityindex < allEthnicity.length; ethnicityindex++) { 
                var nowCount = 0; 
                var nowRace = allRaces[raceindex]; 
                var nowEthnicity = allEthnicity[ethnicityindex]; 
                for (var dataIndex = 0; dataIndex < arrayData.length; dataIndex++) { 
                        if(arrayData[dataIndex][1] == nowRace   &&   arrayData[dataIndex][2] == nowEthnicity){
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
                        if(arrayData[dataIndex][2] == nowEthnicity  &&  arrayData[dataIndex][3] == nowGender ){
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

// //-----------3. Gender to Veteran-----------//

for (var genderindex = 0; genderindex < allGenders.length; genderindex++) {  // choose an armed to look for
        for (var veteranindex = 0; veteranindex < allVeteran.length; veteranindex++) {  // choose a classification to look for
                var nowCount = 0;  // start counting with no values
                var nowGender = allGenders[genderindex];// our chosen gender for this loop
                var nowVeteran = allVeteran[veteranindex]; // our chosen veteran for this loop
                for (var dataIndex = 0; dataIndex < arrayData.length; dataIndex++) { //loop of all data in the array looking for the above race and gender
                        if(arrayData[dataIndex][3] == nowGender  &&  arrayData[dataIndex][4] == nowVeteran ){ // if this data object matches our chosen gender and race
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



// // //-----------4. Veteran to Age-----------//
// for (var veteranindex = 0; veteranindex < allVeteran.length; veteranindex++) { 
//         for (var ageindex = -1; ageindex <= 102; ageindex+=5) {  
//                 var nowCount = 0;  
//                 var nowVeteran = allVeteran[veteranindex];
//                 var nowAge = ageindex; 
//                 for (var dataIndex = 0; dataIndex < arrayData.length; dataIndex++) { 

//                 var inDataAge = arrayData[dataIndex][6];
                       
//                         if(arrayData[dataIndex][4] == nowVeteran &&  inDataAge > nowAge  && inDataAge <= nowAge+5 ){ 
//                                 nowCount++;  
//                               }
//                             }
//                 var miniArray_local = []; 
//                 miniArray_local.push(nowVeteran);
//                 miniArray_local.push((nowAge+1) +'-'+(nowAge+5));
//                 miniArray_local.push(nowCount);
//                 FinalDataArray.push(miniArray_local);
//               }
//             }

// //-----------4. Veteran to Status-----------//
for (var veteranindex = 0; veteranindex < allVeteran.length; veteranindex++) {  
        for (var statusindex = 0; statusindex < allStatus.length; statusindex++) {  
                var nowCount = 0;  // start counting with no values
                var nowVeteran = allVeteran[veteranindex];
                var nowStatus = allStatus[statusindex]; 
                for (var dataIndex = 0; dataIndex < arrayData.length; dataIndex++) { 
                        if(arrayData[dataIndex][4] == nowVeteran  &&  arrayData[dataIndex][8] == nowStatus ){ 
                                nowCount++;  //add one value to our item count
                              }
                            }
                var miniArray_local = []; 
                miniArray_local.push(nowVeteran); 
                miniArray_local.push(nowStatus);
                miniArray_local.push(nowCount);
                // console.log(miniArray_local);
                FinalDataArray.push(miniArray_local);
              }
            }

            // //-----------5. Status to Project 1-----------//
for (var statusindex = 0; statusindex < allStatus.length; statusindex++) {  
        for (var project1index = 0; project1index < allProject1.length; project1index++) {  
                var nowCount = 0;  // start counting with no values
                var nowStatus = allStatus[statusindex];
                var nowProject1 = allProject1[project1index];
                for (var dataIndex = 0; dataIndex < arrayData.length; dataIndex++) { 
                        if(arrayData[dataIndex][8] == nowStatus  &&  arrayData[dataIndex][9] == nowProject1 ){ 
                                nowCount++;  //add one value to our item count
                              }
                            }
                var miniArray_local = []; 
                miniArray_local.push(nowStatus);
                miniArray_local.push(nowProject1); 
                miniArray_local.push(nowCount);
                // console.log(miniArray_local);
                FinalDataArray.push(miniArray_local);
              }
            }

           // //-----------6. Project 1 to Project 2-----------//
for (var project1index = 0; project1index < allProject1.length; project1index++) {  
        for (var project2index = 0; project2index < allProject2.length; project2index++) {  
                var nowCount = 0;  // start counting with no values
                var nowProject1 = allProject1[project1index];
                var nowProject2 = allProject2[project2index];
                for (var dataIndex = 0; dataIndex < arrayData.length; dataIndex++) { 
                        if(arrayData[dataIndex][9] == nowProject1  &&  arrayData[dataIndex][10] == nowProject2 ){ 
                                nowCount++;  //add one value to our item count
                              }
                            }
                var miniArray_local = []; 
                miniArray_local.push(nowProject1);
                miniArray_local.push(nowProject2); 
                miniArray_local.push(nowCount);
                // console.log(miniArray_local);
                FinalDataArray.push(miniArray_local);
              }
            }
          // //-----------7. Project 2 to Project 3-----------//
for (var project2index = 0; project2index < allProject2.length; project2index++) {  
        for (var project3index = 0; project3index < allProject3.length; project3index++) {  
                var nowCount = 0;  // start counting with no values
                var nowProject2 = allProject2[project2index];
                var nowProject3 = allProject3[project3index];
                for (var dataIndex = 0; dataIndex < arrayData.length; dataIndex++) { 
                        if(arrayData[dataIndex][10] == nowProject2  &&  arrayData[dataIndex][11] == nowProject3 ){ 
                                nowCount++;  //add one value to our item count
                              }
                            }
                var miniArray_local = []; 
                miniArray_local.push(nowProject2);
                miniArray_local.push(nowProject3); 
                miniArray_local.push(nowCount);
                // console.log(miniArray_local);
                FinalDataArray.push(miniArray_local);
              }
            }

          // //-----------8. Project 3 to Permanent Housing-----------//
for (var project3index = 0; project3index < allProject3.length; project3index++) {  
        for (var PermanentHousingindex = 0; PermanentHousingindex < allPermanentHousing.length; PermanentHousingindex++) {  
                var nowCount = 0;  // start counting with no values
                var nowProject3 = allProject3[project3index];
                var nowPermanentHousing = allPermanentHousing[PermanentHousingindex];
                
                for (var dataIndex = 0; dataIndex < arrayData.length; dataIndex++) { 
                        if(arrayData[dataIndex][11] == nowProject3  &&  arrayData[dataIndex][12] == nowPermanentHousing ){ 
                                nowCount++;  //add one value to our item count
                              }
                            }
                var miniArray_local = []; 
                miniArray_local.push(nowProject3);
                miniArray_local.push(nowPermanentHousing); 
                miniArray_local.push(nowCount);
                // console.log(miniArray_local);
                FinalDataArray.push(miniArray_local);
              }
            }
//             // console.log('IN THE END we found this:');
//             // console.log(FinalDataArray);

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