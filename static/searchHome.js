const PublishCourses = document.getElementsByClassName("published_search_course");

const CoursesArray = [];

for (let i in PublishCourses){
    if (i <= PublishCourses.length){
    const CoursesDict = {};
    CoursesDict['divInput'] = PublishCourses[i].innerHTML;
    CoursesDict['word'] = PublishCourses[i].innerText.split('\n');
    CoursesArray.push(CoursesDict)}
} 
const CourseSearch=(courseName)=>{
    console.log(courseName)
    document.getElementById('all_courses').innerHTML='';
    document.getElementById('result').innerHTML='';
    const main = document.createElement('div');
    document.getElementById('result').appendChild(main);
    main.className = "all_courses";   
    const courses = CoursesArray.filter(course => course.word[0].toLowerCase().startsWith(courseName));
    courses.forEach(function(item, index){
        var result = document.createElement('div');
        result.className = "published_search_course";
        result.innerHTML = item.divInput; 
        main.append(result);
    })
}