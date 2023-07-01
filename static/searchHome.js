const HomePublishCourses = document.getElementsByClassName("published_search_course");

const HomeCoursesArray = [];

for (let i in HomePublishCourses){
    if (i <= HomePublishCourses.length){
    const HomeCoursesDict = {};
    HomeCoursesDict['divInput'] = HomePublishCourses[i].innerHTML;
    HomeCoursesDict['word'] = HomePublishCourses[i].innerText.split('\n');
    HomeCoursesArray.push(HomeCoursesDict)}
} 
const HomeCoursesSearch=(courseName)=>{
    console.log(courseName)
    document.getElementById('all_courses').innerHTML='';
    document.getElementById('result').innerHTML='';
    const main = document.createElement('div');
    document.getElementById('result').appendChild(main);
    main.className = "all_courses";   
    const courses = HomeCoursesArray.filter(course => course.word[0].toLowerCase().startsWith(courseName));
    courses.forEach(function(item, index){
        var result = document.createElement('div');
        result.className = "published_search_course";
        result.innerHTML = item.divInput; 
        main.append(result);
    })
}