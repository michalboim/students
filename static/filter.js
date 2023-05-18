const loction = document.getElementsByClassName("choose_loction");
const PublishCourses = document.getElementsByClassName("published_course");

const LoctionArray = [];
for (let i in loction){
    if (i <= loction.length){
    const LoctionDict = {};
    LoctionDict['divInput'] = loction[i].innerHTML;
    LoctionDict['word'] = loction[i].innerText;
    LoctionArray.push(LoctionDict)}
} 
const CoursesArray = [];
for (let i in PublishCourses){
    if (i <= PublishCourses.length){
    const CoursesDict = {};
    CoursesDict['divInput'] = PublishCourses[i].innerHTML;
    CoursesDict['word'] = PublishCourses[i].innerText.split('\n');
    CoursesArray.push(CoursesDict)}
} 

const loctionSearch=()=>{
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
const CourseSearch=(courseName)=>{
    document.getElementById('published_form').innerHTML='';
    document.getElementById('result').innerHTML='';
    const main = document.createElement('div');
    document.getElementById('result').appendChild(main);
    main.className = "published_form";   
    const courses = CoursesArray.filter(course => course.word[0].toLowerCase().startsWith(courseName));
    courses.forEach(function(item, index){
        var result = document.createElement('div');
        result.className = "published_course";
        result.innerHTML = item.divInput; 
        main.append(result);
    })
}


