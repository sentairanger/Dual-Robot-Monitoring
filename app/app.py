# import libraries
from flask import Flask, render_template, request, json
from prometheus_flask_exporter import PrometheusMetrics
from gpiozero import OutputDevice, AngularServo, PWMOutputDevice, LED
from gpiozero.pins.pigpio import PiGPIOFactory
import logging
from jaeger_client import Config
from os import getenv

# Define the jaeger host
JAEGER_HOST = getenv('JAEGER_HOST', 'localhost')

# Define the Jaeger function
def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
            'local_agent': {'reporting_host': JAEGER_HOST},
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()

tracer = init_tracer('stop-service')

# Define the factories
factory = PiGPIOFactory(host='192.168.0.21')
factory2 = PiGPIOFactory(host='192.168.0.23')

# Define both robots
en_1 = PWMOutputDevice(12, pin_factory=factory)
en_2 = PWMOutputDevice(26, pin_factory=factory)
motor_in1 = OutputDevice(13,  pin_factory = factory)
motor_in2 = OutputDevice(21,  pin_factory = factory)
motor_in3 = OutputDevice(17,  pin_factory = factory)
motor_in4 = OutputDevice(27,  pin_factory = factory)

pin1 = OutputDevice(7,  pin_factory = factory2)
pin2 = OutputDevice(8,  pin_factory = factory2)
pin3 = OutputDevice(9,  pin_factory = factory2)
pin4 = OutputDevice(10,  pin_factory = factory2)

#Define the eyes
linus_eye = LED(16, pin_factory=factory)
torvalds_eye = LED(25, pin_factory=factory2)

# Define the servo
angular_servo = AngularServo(22, min_angle=-90, max_angle=90, pin_factory=factory)
angular_servo2 = AngularServo(23, min_angle=-90, max_angle=90, pin_factory=factory)

# Define app and the metrics endpoint
app = Flask(__name__)

metrics = PrometheusMetrics(app)
metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)

# Apply the same metric to all of the endpoints
endpoint_counter = metrics.counter(
    'endpoint_counter', 'Request count by endpoints',
    labels={'endpoint': lambda: request.endpoint}
)

def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug server')
    func()

# gracefully shutdown the app
@app.route('/shutdown', methods=['GET'])
def shutdown_server():
    shutdown()
    return 'Server shutting down'



@app.route('/status')
@endpoint_counter
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Status request successfull')
    return response

@app.route('/')
@endpoint_counter
def index():
    return render_template('dual-robot.html')

# Linus movement
@app.route('/forward')
@endpoint_counter
def forward():
    motor_in1.on()
    motor_in2.off()
    motor_in3.on()
    motor_in4.off()
    return render_template('dual-robot.html')

@app.route('/backward')
@endpoint_counter
def backward():
    motor_in1.off()
    motor_in2.on()
    motor_in3.off()
    motor_in4.on()
    return render_template('dual-robot.html')

@app.route('/left')
@endpoint_counter
def left():
    motor_in1.off()
    motor_in2.on()
    motor_in3.on()
    motor_in4.off()
    return render_template('dual-robot.html')

@app.route('/right')
@endpoint_counter
def right():
    motor_in1.on()
    motor_in2.off()
    motor_in3.off()
    motor_in4.on()
    return render_template('dual-robot.html')

@app.route('/stop')
@endpoint_counter
def stop():
    motor_in1.off()
    motor_in2.off()
    motor_in3.off()
    motor_in4.off()
    return render_template('dual-robot.html')

# Torvalds movement

@app.route('/north')
@endpoint_counter
def north():
    pin1.off()
    pin2.on()
    pin3.on()
    pin4.off()
    return render_template('dual-robot.html')

@app.route('/south')
@endpoint_counter
def south():
    pin1.on()
    pin2.off()
    pin3.off()
    pin4.on()
    return render_template('dual-robot.html')

@app.route('/west')
@endpoint_counter
def west():
    pin1.on()
    pin2.off()
    pin3.on()
    pin4.off()
    return render_template('dual-robot.html')

@app.route('/east')
@endpoint_counter
def east():
    pin1.off()
    pin2.on()
    pin3.off()
    pin4.on()
    return render_template('dual-robot.html')

@app.route('/stoptwo')
@endpoint_counter
def stoptwo():
    pin1.off()
    pin2.off()
    pin3.off()
    pin4.off()
    return render_template('dual-robot.html')

# Eye blink

@app.route('/linuson')
@endpoint_counter
def linuson():
    with tracer.start_span('linus-eye') as span:
        linus_eye.on()
    return render_template('dual-robot.html')

@app.route('/linusoff')
@endpoint_counter
def linusoff():
    linus_eye.off()
    return render_template('dual-robot.html')

@app.route('/torvaldson')
@endpoint_counter
def torvaldson():
    with tracer.start_span('torvalds-eye') as span:
        torvalds_eye.on()
    return render_template('dual-robot.html')

@app.route('/torvaldsoff')
@endpoint_counter
def torvaldsoff():
    torvalds_eye.off()
    return render_template('dual-robot.html')

# Servo movement

@app.route('/servoarm', methods=['POST'])
@endpoint_counter
def servoarm():
    slider1 = request.form["degree"]
    slider2 = request.form["degree2"]
    angular_servo.angle = int(slider1)
    angular_servo2.angle = int(slider2)
    return render_template('dual-robot.html')

# PWM speed

@app.route('/motorpwm', methods=['POST'])
@endpoint_counter
def motorpwm():
    slider3 = request.form["speed"]
    slider4 = request.form["speed2"]
    en_1.value = int(slider3) / 10
    en_2.value = int(slider4) / 10
    return render_template('dual-robot.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
