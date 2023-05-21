let i=0
async function HomeCourses(){
    let response=await fetch('published_courses');
    let data=await response.json();
    let html="";
    console.log(data[1])

}
let courses = HomeCourses();
console.log(courses)