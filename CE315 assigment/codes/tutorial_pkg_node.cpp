//import our libraries.
#include <functional>
#include <memory>
#include <string>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "geometry_msgs/msg/pose.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include <fstream>
#include <time.h>
#include <iomanip>
#include "sensor_msgs/msg/laser_scan.hpp"
using namespace std::chrono_literals;
using namespace std;

//include our files for odmetry data, velcoity data,data for each laser and--- 
//---laser mapping data.
ofstream odomTrajFile;
ofstream odomVelFile;
ofstream laserFile;
ofstream laserMapFile;

struct EulerAngles
{
	double roll, pitch, yaw;
};	// yaw is what you want, i.e. Th
struct Quaternion
{
	double w, x, y, z;
};

EulerAngles ToEulerAngles(Quaternion q)
{
	// for calculating Th
	EulerAngles angles;

	// roll (x-axis rotation)
	double sinr_cosp = +2.0 *(q.w *q.x + q.y *q.z);
	double cosr_cosp = +1.0 - 2.0 *(q.x *q.x + q.y *q.y);
	angles.roll = atan2(sinr_cosp, cosr_cosp);

	// pitch (y-axis rotation)
	double sinp = +2.0 *(q.w *q.y - q.z *q.x);

	if (fabs(sinp) >= 1)
		angles.pitch = copysign(M_PI / 2, sinp);	//use 90 degrees if out of range
	else
		angles.pitch = asin(sinp);
	// yaw (z-axis rotation)
	double siny_cosp = +2.0 *(q.w *q.z + q.x *q.y);
	double cosy_cosp = +1.0 - 2.0 *(q.y *q.y + q.z *q.z);
	angles.yaw = atan2(siny_cosp, cosy_cosp);
	return angles;
}

//set all our functions and other variables needed like robot velocity.....etc. 
class Stopper: public rclcpp::Node
{
	public:

	/*velocity control variables*/
	constexpr const static double FORWARD_SPEED_LOW = 0.1;
	constexpr const static double FORWARD_SPEED_MIDDLE = 0.3;
	constexpr const static double FORWARD_SPEED_HIGH = 0.5;
	constexpr const static double FORWARD_SPEED_STOP = 0;
	constexpr const static double TURN_LEFT_SPEED_LOW = 0.3;
	constexpr const static double TURN_LEFT_SPEED_MIDDLE = 0.6;
	constexpr const static double TURN_LEFT_SPEED_HIGH = 1.0;
	constexpr const static double TURN_RIGHT_SPEED_LOW = -0.3;
	constexpr const static double TURN_RIGHT_SPEED_MIDDLE = -0.6;
	constexpr const static double TURN_RIGHT_SPEED_HIGH = -1.0;

	/*class constructor */
	Stopper(): Node("Stopper"), count_(0)
	{
		publisher_ = this->create_publisher<geometry_msgs::msg::Twist > ("cmd_vel", 10);
		odomSub_ = this->create_subscription<nav_msgs::msg::Odometry > ("odom", 10,
			std::bind(&Stopper::odomCallback, this, std::placeholders::_1));
		laserScan_ = this->create_subscription<sensor_msgs::msg::LaserScan > ("scan", 10,
			std::bind(&Stopper::scanCallback, this, std::placeholders::_1));
	};

	/*moving functions */
	void startMoving();
	void moveStop();
	void moveForward(double forwardSpeed);
	void moveRight(double turn_right_speed);
	void moveForwardRight(double forwardSpeed, double turn_right_speed);
	void odomCallback(const nav_msgs::msg::Odometry::SharedPtr odomMsg);
	double PositionX = 0.3, PositionY = 0.3, homeX = 0.3, homeY = 0.3;
	double robVelocity;
	int numberOfCycle = 0;
	void scanCallback(const sensor_msgs::msg::LaserScan::SharedPtr scan);
	double frontRange, mleftRange, leftRange, rightRange, mrightRange;
	int laser_index = 0;	// index the laser scan data
	Quaternion robotQuat;
	EulerAngles robotAngles;
	double robotHeadAngle;
	double leftAngle = M_PI / 2, mleftAngle = M_PI / 4, frontAngle = 0;
	double mrightAngle = -M_PI / 4, rightAngle = -M_PI / 2;
	void transformMapPoint(ofstream &fp, double laserRange, double laserTh,
		double robotTh, double robotX, double robotY);
	int stage = 1;

	private:

		// Publisher to the robot's velocity command topic.
		rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
	rclcpp::TimerBase::SharedPtr timer_;
	size_t count_;

	//Subscriber to robot’s odometry topic.
	rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odomSub_;
	rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr laserScan_;
}; 

//function to move forward.
void Stopper::moveForward(double forwardSpeed)
{
	auto msg = geometry_msgs::msg::Twist();
	msg.linear.x = forwardSpeed;
	publisher_->publish(msg);
}

//function to stop.
void Stopper::moveStop()
{
	auto msg = geometry_msgs::msg::Twist();
	msg.linear.x = FORWARD_SPEED_STOP;
	publisher_->publish(msg);
}

//function to turn  to the right. 
void Stopper::moveRight(double turn_right_speed)
{
	auto msg = geometry_msgs::msg::Twist();
	msg.angular.z = turn_right_speed;
	publisher_->publish(msg);
}

//function to move forward while turning to the right. 
void Stopper::moveForwardRight(double forwardSpeed, double turn_right_speed)
{
	auto msg = geometry_msgs::msg::Twist();
	msg.linear.x = forwardSpeed;
	msg.angular.z = turn_right_speed;
	publisher_->publish(msg);
}

//function for odometry 
void Stopper::odomCallback(const nav_msgs::msg::Odometry::SharedPtr odomMsg)
{
	PositionX = odomMsg->pose.pose.position.x + homeX;
	PositionY = odomMsg->pose.pose.position.y + homeY;
	RCLCPP_INFO(this->get_logger(), "RobotPostion: %.2f, %.2f", PositionX, PositionY);
	RCLCPP_INFO(this->get_logger(), "Robot stage: %d ", stage);
	//code for moving the robot usuing odmetry data
	//if commented, uncomment to run robot movment with odometry and comment laser movment 
/*	 
	stage = 0; 
	if (PositionY < 1.20 && PositionX < 0.38)
{
	stage = 1;
	moveForward(FORWARD_SPEED_MIDDLE);
}
else if (PositionX < 0.80)
{
	stage = 2;
	moveForwardRight(FORWARD_SPEED_MIDDLE, TURN_RIGHT_SPEED_MIDDLE);
}
else if (PositionX < 1.20)
{
	stage = 3;
	moveForward(FORWARD_SPEED_HIGH);
}
else if (PositionX < 1.80)
{
	stage = 4;
	moveForwardRight(FORWARD_SPEED_MIDDLE, TURN_RIGHT_SPEED_MIDDLE);
}
else if (PositionX < 2.25)
{
	stage = 5;
	moveForward(FORWARD_SPEED_MIDDLE);
}
else
{
	stage = 6;
	moveStop();
}
*/	
	robVelocity = odomMsg->twist.twist.linear.x;	//get velocity 
	odomVelFile << numberOfCycle++ << " " << robVelocity << endl;	//insert velocity into file  
	odomTrajFile << PositionX << " " << PositionY << endl;	// insert trajectory into file 
	robotQuat.x = odomMsg->pose.pose.orientation.x;
	robotQuat.y = odomMsg->pose.pose.orientation.y;
	robotQuat.z = odomMsg->pose.pose.orientation.z;
	robotQuat.w = odomMsg->pose.pose.orientation.w;
	robotAngles = ToEulerAngles(robotQuat);
	robotHeadAngle = robotAngles.yaw;
}

//function for laser
void Stopper::scanCallback(const sensor_msgs::msg::LaserScan::SharedPtr scan)
{
	leftRange = scan->ranges[300];	// get a range reading at the left angle
	mleftRange = scan->ranges[250];	// get a range reading at the front-left angle
	frontRange = scan->ranges[200];	// get a range reading at the front angle
	mrightRange = scan->ranges[150];	// get a range reading at the front-right angle
	rightRange = scan->ranges[100];	// get the range reading at the right angle
	laserFile << leftRange << "," << mleftRange << "," << frontRange << "," <<
		mrightRange << "," << rightRange << "," << laser_index++ << endl;	//insert laser ranges to fie

	transformMapPoint(laserMapFile, frontRange, frontAngle, robotHeadAngle, PositionX, PositionY);	//insert maplaser file front 
	transformMapPoint(laserMapFile, mleftRange, mleftAngle, robotHeadAngle,
		PositionX, PositionY);	//insert maplaser file mleft 
	transformMapPoint(laserMapFile, leftRange, leftAngle, robotHeadAngle,
		PositionX, PositionY);	//insert maplaser file left 
	transformMapPoint(laserMapFile, rightRange, rightAngle, robotHeadAngle,
		PositionX, PositionY);	//insert maplaser file right 
	transformMapPoint(laserMapFile, mrightRange, mrightAngle, robotHeadAngle,
		PositionX, PositionY);	//insert maplaser file mright

	//function for controloing robot usuing laser (case3-5 = my code)
	//if commented, uncomment to run robot movment with laser and comment odometry movment 

	switch (stage)
	{
		case 1:
			if (frontRange > 1.3)
				moveForward(FORWARD_SPEED_HIGH);
			else stage = 2;
			break;
		case 2:
			if (mleftRange < 1.4)
				moveForwardRight(FORWARD_SPEED_MIDDLE, TURN_RIGHT_SPEED_MIDDLE);
			else stage = 3;
			break;
		case 3:
			if (frontRange > 0.6)
				moveForward(FORWARD_SPEED_HIGH);
			else stage = 4;
			break;
		case 4:
			if (rightRange > 0.3)
				moveForwardRight(FORWARD_SPEED_MIDDLE, TURN_RIGHT_SPEED_MIDDLE);
			else stage = 5;
			break;
		case 5:
			if (frontRange > 0.4)
				moveForward(FORWARD_SPEED_MIDDLE);
			else stage = 6;
			break;
		case 6:
			moveStop();
			break;
	}
	
}

//transforms robot data into gloabal data
void Stopper::transformMapPoint(ofstream &fp, double laserRange, double laserTh,
	double robotTh, double robotX, double robotY)
{
	double transX, transY;
	transX = laserRange* cos(robotTh + laserTh) + robotX;
	transY = laserRange* sin(robotTh + laserTh) + robotY;
	if (transX < 0) transX = homeX;
	else transX += homeX;
	if (transY < 0) transY = homeX;
	else transY += homeY;
	fp << transX << ", " << transY << endl;
}

//opens files and saves the data into the files while robot is moving  
void Stopper::startMoving()
{
	odomTrajFile.open("/ufs/servg00/users/hh18564/M-Drive/ros_workspace/src/tutorial_pkg/data/odomTrajData.csv", ios::trunc);	//open TrajData
	odomVelFile.open("/ufs/servg00/users/hh18564/M-Drive/ros_workspace/src/tutorial_pkg/data/odomVelData.csv", ios::trunc);	//open VelData
	laserFile.open("/ufs/servg00/users/hh18564/M-Drive/ros_workspace/src/tutorial_pkg/data/laserData.csv", ios::trunc);	//open LaserData
	laserMapFile.open("/ufs/servg00/users/hh18564/M-Drive/ros_workspace/src/tutorial_pkg/data/laserMapData.csv", ios::trunc);	//open LaseMapData
	RCLCPP_INFO(this->get_logger(), "Start moving");
	rclcpp::WallRate loop_rate(10);
	while (rclcpp::ok())
	{
		auto node = std::make_shared<Stopper> ();
		rclcpp::spin(node);	// update
		loop_rate.sleep();	// wait delta time
	}
	odomTrajFile.close();	//close TrajData
	odomVelFile.close();	//close VelData
	laserFile.close();	//close LaserData
	laserMapFile.close();	//close LaseMapData
}

//main fucntion 
int main(int argc, char *argv[])
{
	rclcpp::init(argc, argv);
	Stopper stopper;
	stopper.startMoving();
	return 0;
}
