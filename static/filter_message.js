const loction = document.getElementsByClassName("choose_loction");
const LoctionArray = [];
for (let i in loction){
    if (i <= loction.length){
    const LoctionDict = {};
    LoctionDict['divInput'] = loction[i].innerHTML;
    LoctionDict['word'] = loction[i].innerText;
    LoctionArray.push(LoctionDict)}
} 
console.log(LoctionArray);
const mySearch=()=>{
    document.getElementById('message_loction').innerHTML='';
    document.getElementById('result').innerHTML='';
    const main = document.createElement('div');
    document.getElementById('result').appendChild(main);
    main.className = "message_loction";   
    const searchVal = document.getElementById('search').value.toLowerCase();
    const courses = LoctionArray.filter(course => course.word.toLowerCase().startsWith(searchVal));
    courses.forEach(function(item, index){
        var result = document.createElement('div');
        result.className = "choose_loction";
        result.innerHTML = item.divInput; 
        main.append(result);
    })
}


